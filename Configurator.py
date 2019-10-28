import json
from utils import mkdir, chmod
from mako.template import Template

from Router import Router


class Configurator:

    def __init__(self):
        self.routers = []
        self.config = json.load(open("config.json", "r"))
        mkdir(self.config.get("config_folder"))

    def create_routers_list(self):
        print("Creating routers list:", end="")
        try:
            for router_json in self.config.get("routers", []):
                router = Router.from_json(router_json)
                self.routers.append(router)
                print("\t", router.name, "v", end="")
        except FileNotFoundError as err:
            print("Unable to open configuration file", err, end="")
            exit(-1)
        print()

    def create_ospf_config(self):
        print("Creating OSPF configs:", end="")
        for router in self.routers:
            print("\t", router.name, end="")
            ospf_template = Template(open('mako-templates/ospf.mako').read())
            config = ospf_template.render(router=router)
            mkdir("{config_folder}/{router_name}".format(
                config_folder=self.config.get("config_folder"),
                router_name=router.name
            ))
            fd = open("{config_folder}/{router_name}/{router_name}_ospf.conf".format(
                config_folder=self.config.get("config_folder"),
                router_name=router.name
            ), "w")
            fd.write(config)
            fd.close()
            print(" v", end="")
        print()

    def create_start_config(self):
        print("Creating START configs:", end="")
        for router in self.routers:
            print("\t", router.name, end="")
            start_template = Template(open('mako-templates/start.mako').read())
            config = start_template.render(router=router)
            fd = open("{config_folder}/{router_name}_start".format(
                config_folder=self.config.get("config_folder"),
                router_name=router.name
            ), "w")
            fd.write(config)
            fd.close()
            chmod("{config_folder}/{router_name}_start".format(
                config_folder=self.config.get("config_folder"),
                router_name=router.name
            ))
            print(" v",end="")
        print()

    def create_boot_config(self):
        print("Creating BOOT scripts:", end="")
        for router in self.routers:
            print("\t", router.name, end="")
            start_template = Template(open('mako-templates/boot.mako').read())
            config = start_template.render()
            fd = open("{config_folder}/{router_name}_boot".format(
                config_folder=self.config.get("config_folder"),
                router_name=router.name
            ), "w")
            fd.write(config)
            fd.close()
            chmod("{config_folder}/{router_name}_boot".format(
                config_folder=self.config.get("config_folder"),
                router_name=router.name
            ))
            print(" ✓", end="")
        print()

    def create_config(self):
        self.create_routers_list()
        self.create_ospf_config()
        self.create_start_config()
        self.create_boot_config()
        print("===== DONE =====")
