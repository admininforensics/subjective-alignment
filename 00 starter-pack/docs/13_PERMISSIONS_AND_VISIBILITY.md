# Permissions and Visibility

## Roles

| Role | Can Complete Assessment | Can View Own Results | Can View Others |
|---|---:|---:|---:|
| RESPONDENT | Yes | Yes | No |
| MANAGER | Optional | Yes | Assigned respondents |
| ORG_ADMIN | Optional | Yes | Organisation users |
| SUPER_ADMIN | Yes | Yes | All users |

## Rules

- A respondent can only access their own session.
- A manager can only access respondents assigned to them or in their reporting group.
- An organisation admin can access all users in their organisation.
- A super admin can access all organisations.
- Permissions must be enforced in the backend, not only in the frontend.

## Recommended Model Addition

```python
class ManagerAssignment(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managed_assignments")
    respondent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="manager_assignments")

    class Meta:
        unique_together = ("manager", "respondent")
```
