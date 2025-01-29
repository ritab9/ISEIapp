def is_in_group(user, group):
    return user.groups.filter(name=group).exists()

def is_in_any_group(user, groups):
    return user.groups.filter(name__in=groups).exists()