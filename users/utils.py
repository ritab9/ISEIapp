def is_in_group(user, group):
    return user.groups.filter(name=group).exists()