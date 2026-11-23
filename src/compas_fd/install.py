from compas.plugins import plugin


@plugin(category="install", priority=1)
def installable_rhino_packages() -> list[str]:
    return ["compas_fd"]
