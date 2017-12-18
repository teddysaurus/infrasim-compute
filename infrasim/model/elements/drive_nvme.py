'''
*********************************************************
Copyright @ 2015 EMC Corporation All Rights Reserved
*********************************************************
'''
# -*- coding: utf-8 -*-


from infrasim import ArgsNotCorrect
from infrasim import helper
from infrasim.model.elements.drive import CBaseDrive


class NVMeController(CBaseDrive):
    def __init__(self, dev_info):
        super(NVMeController, self).__init__()
        self._name = "nvme"
        self.prefix = "nvme"
        self._drive_info = dev_info
        self._cmb_size_in_mb = 0
        self._controller_info = dev_info
        self.__controller_index = 0
        self.__bus = None
        self.__config_file = None

    def get_uniq_name(self):
        return "{}".format(self.__controller_index)

    @property
    def controller_index(self):
        return self.__controller_index

    @controller_index.setter
    def controller_index(self, idx):
        self.__controller_index = idx

    def init(self):
        super(NVMeController, self).init()
        self._cmb_size_in_mb = self._drive_info.get("cmb_size", 256)
        if not self.serial:
            self.serial = helper.random_serial()

        if self._drive_info.get("bus"):
            self.__bus = self._drive_info.get("bus")

        self.__config_file = self._drive_info.get("config_file")

    def precheck(self):
        # Since QEMU support CMB size in MB, we recognize 1k, 4k
        # CMB size as invalid here.
        if self._cmb_size_in_mb not in [1, 16, 256, 4096, 65536]:
            raise ArgsNotCorrect("[NVMe{}] CMB size {} is invalid".
                                  format(self.__controller_index, self._cmb_size_in_mb))

    def handle_parms(self):
        super(NVMeController, self).handle_parms()

        drive_id = "{}-{}".format(self.prefix,
                                  self.controller_index)

        # Host option
        self._host_opt["if"] = "none"
        self._host_opt["id"] = drive_id

        self.add_option(self.build_host_option(**self._host_opt))

        # Device option
        self._dev_attrs["drive"] = drive_id
        self._dev_attrs["id"] = "dev-{}".format(self._dev_attrs["drive"])
        self._dev_attrs["cmb_size_mb"] = self._cmb_size_in_mb
        if self.__bus:
            self._dev_attrs["bus"] = self.__bus

        if self.__config_file:
            self._dev_attrs["config_file"] = self.__config_file

        self.add_option(self.build_device_option(self._name, **self._dev_attrs))