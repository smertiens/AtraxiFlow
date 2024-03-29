#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import json
import logging
import os
import platform

__all__ = ['PreferencesProvider']


class PreferencesProvider:

    def __init__(self):
        self.settings = {}
        self.load()

    def get(self, name, default=None):
        if name in self.settings:
            return self.settings[name]
        elif default is not None:
            return default

    def set(self, name, val):
        self.settings[name] = val

    def load(self):
        if not os.path.exists(self.get_settings_file('settings.json')):
            return

        with open(self.get_settings_file('settings.json'), 'r') as f:
            try:
                obj = json.load(f)
                self.settings = obj
            except json.JSONDecodeError:
                self.get_logger().error('Unable to read settings file')
                return

    def save(self):
        with open(self.get_settings_file('settings.json'), 'w') as f:
            json.dump(self.settings, f)

        self.get_logger().debug('Settings saved')

    def get_settings_file(self, fname=''):

        if 'AXFLOW_SETTINGS_FILE' in os.environ:
            return os.environ['AXFLOW_SETTINGS_FILE']

        user_dir = os.path.expanduser('~')

        if platform.system() == 'Windows':
            user_dir = os.path.join(user_dir, "atraxiflow")
        else:
            user_dir = os.path.join(user_dir, ".atraxiflow")

        if not os.path.exists(user_dir):
            self.get_logger().info('User dir does not exist. Creating {0}'.format(user_dir))
            os.makedirs(user_dir)

        return os.path.join(user_dir, fname)

    def get_logger(self):
        return logging.getLogger('core')
