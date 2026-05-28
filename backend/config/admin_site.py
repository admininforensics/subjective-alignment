from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from django.contrib import admin
from django.http import Http404, HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import path


@dataclass(frozen=True)
class CsvFileInfo:
    name: str
    path: Path
    size_bytes: int


class SubjectiveAlignmentAdminSite(admin.AdminSite):
    site_header = "Subjective Alignment Admin"
    site_title = "Subjective Alignment Admin"
    index_title = "Admin"

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path("seed-csvs/", self.admin_view(self.seed_csvs_view), name="seed-csvs"),
            path(
                "seed-csvs/download/<path:filename>/",
                self.admin_view(self.seed_csvs_download),
                name="seed-csvs-download",
            ),
        ]
        return extra + urls

    def _data_dir(self) -> Path:
        # backend/ -> repo root -> data/
        return Path(__file__).resolve().parents[2] / "data"

    def _list_csvs(self) -> list[CsvFileInfo]:
        data_dir = self._data_dir()
        if not data_dir.exists() or not data_dir.is_dir():
            return []

        files: list[CsvFileInfo] = []
        for p in sorted(data_dir.glob("*.csv")):
            try:
                stat = p.stat()
            except FileNotFoundError:
                continue
            files.append(CsvFileInfo(name=p.name, path=p, size_bytes=stat.st_size))
        return files

    def seed_csvs_view(self, request: HttpRequest) -> HttpResponse:
        files = self._list_csvs()

        preview: dict[str, dict] = {}
        for f in files:
            try:
                with f.path.open("r", encoding="mac_roman", newline="") as fh:
                    reader = csv.reader(fh)
                    rows = []
                    for _ in range(6):  # header + first 5 rows
                        try:
                            rows.append(next(reader))
                        except StopIteration:
                            break
                preview[f.name] = {"rows": rows, "error": None}
            except Exception as e:  # noqa: BLE001 - admin diagnostic
                preview[f.name] = {"rows": [], "error": str(e)}

        context = {
            **self.each_context(request),
            "title": "Seed CSVs (from /data)",
            "files": files,
            "preview": preview,
            "data_dir": str(self._data_dir()),
        }
        return TemplateResponse(request, "admin/seed_csvs.html", context)

    def seed_csvs_download(self, request: HttpRequest, filename: str) -> HttpResponse:
        if "/" in filename or "\\" in filename or ".." in filename:
            raise Http404()

        file_path = self._data_dir() / filename
        if not file_path.exists() or not file_path.is_file() or file_path.suffix.lower() != ".csv":
            raise Http404()

        data = file_path.read_bytes()
        resp = HttpResponse(data, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{file_path.name}"'
        return resp


admin_site = SubjectiveAlignmentAdminSite(name="sa_admin")

# Register all models on this admin site.
# (Import at end to avoid import-order issues.)
from config import admin_register as _admin_register  # noqa: F401,E402

