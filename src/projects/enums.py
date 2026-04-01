from enum import Enum


class ProjectRole(Enum): 
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"