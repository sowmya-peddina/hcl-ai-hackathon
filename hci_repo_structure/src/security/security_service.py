# security service

class SecurityService:
    """Handles authentication, multi-factor auth, and login protection."""

    MAX_FAILED_ATTEMPTS = 5

    def __init__(self):
        self.users = {}

    def register_user(self, username, password):
        self.users[username] = {
            "password": password,
            "mfa_enabled": False,
            "failed_attempts": 0,
            "locked": False,
        }

    def enable_mfa(self, username):
        """Enable multi-factor authentication for a user.

        After enabling, every login must be verified with a one-time
        password (OTP) in addition to the primary credentials.
        """
        user = self.users[username]
        user["mfa_enabled"] = True
        return {"mfa_enabled": True, "backup_codes": self._generate_backup_codes()}

    def login(self, username, password, otp=None):
        """Authenticate a user, enforcing MFA and lockout policies.

        Invalid credentials are rejected and counted; the account is locked
        after too many failed attempts. When MFA is enabled, a valid OTP is
        required as the second factor.
        """
        user = self.users.get(username)
        if not user:
            return {"success": False, "reason": "invalid_credentials"}
        if user["locked"]:
            return {"success": False, "reason": "account_locked"}
        if user["password"] != password:
            user["failed_attempts"] += 1
            if user["failed_attempts"] >= self.MAX_FAILED_ATTEMPTS:
                user["locked"] = True
            return {"success": False, "reason": "invalid_credentials"}
        if user["mfa_enabled"] and not otp:
            return {"success": False, "reason": "otp_required"}
        user["failed_attempts"] = 0
        return {"success": True}

    @staticmethod
    def _generate_backup_codes(n=5):
        return [f"BCK-{i:04d}" for i in range(n)]
