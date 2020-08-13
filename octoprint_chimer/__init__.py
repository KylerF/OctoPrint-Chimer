# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.
import glob
import os

import octoprint.plugin

class ChimerPlugin(octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.TemplatePlugin):

	##~~ StartupPlugin mixin

	def on_after_startup(self):
		mute = self._settings.get_boolean(["mute"])
		self._logger.info("mute = {mute}".format(**locals()))

	##~~ TemplatePlugin mixin

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	def get_template_vars(self):
		# Read all available GCODE chimes
		path = os.getcwd()
		none_option = ["None"]
		avail_chimes = sorted(glob.glob('{0}/gcode/*.gcode'.format(path)))
		avail_chimes = [os.path.splitext(os.path.basename(chime))[0] for chime in avail_chimes]
		all_chimes = none_option + avail_chimes

		return dict(
			chimes=all_chimes,
			after_printer_connected_chime=self._settings.get(["after_printer_connected_chime"]),
			before_printer_disconnected_chime=self._settings.get(["before_printer_disconnected_chime"]),
			before_print_started_chime=self._settings.get(["before_print_started_chime"]),
			after_print_cancelled_chime=self._settings.get(["after_print_cancelled_chime"]),
			after_print_done_chime=self._settings.get(["after_print_done_chime"]),
			after_print_paused=self._settings.get(["after_print_paused"]),
			before_print_resumed=self._settings.get(["before_print_resumed"])
		)
			

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			mute=False,
			after_printer_connected_chime="None",
			before_printer_disconnected_chime="None",
			before_print_started_chime="None", 
			after_print_cancelled_chime="None",
			after_print_done_chime="None",
			after_print_paused_chime="None",
			before_print_resumed_chime="None"
		)

	def on_settings_save(self, data):
		old_mute = self._settings.get_boolean(["mute"])
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		new_mute = self._settings.get_boolean(["mute"])
		
		if old_mute != new_mute:
			self._logger.info("mute changed from {old_mute} to {new_mute}".format(**locals()))

		old_chime = self._settings.get(["after_printer_connected_chime"])
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		new_chime = self._settings.get(["after_printer_connected_chime"])
		
		if old_chime != new_chime:
			self._logger.info("mute changed from {old_chime} to {new_chime}".format(**locals()))



	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			#js=["js/chimer.js"],
			#css=["css/chimer.css"],
			#less=["less/chimer.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			chimer=dict(
				displayName="Chimer",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="KylerF",
				repo="OctoPrint-Chimer",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/KylerF/OctoPrint-Chimer/archive/{target_version}.zip"
			)
		)

	def gcode_script_hook(self, comm, script_type, script_name, *args, **kwargs):
		if not script_type == "gcode":
			return None

		# Return if muted
		if self._settings.get_boolean(["mute"]):
			return None
	
		prefix, postfix = self.retrieve_chime(script_name)

		if postfix is None:
			return None

		return prefix, postfix

	def retrieve_chime(self, script_name):
		# Determine the desired setting
		if script_name == "afterPrinterConnected":
			setting = "after_printer_connected_chime"
		elif script_name == "beforePrinterDisconnected":
			setting = "before_printer_disconnected_chime"
		elif script_name == "beforePrintStarted":
			setting = "before_print_started_chime"
		elif script_name == "afterPrintCancelled":
			setting = "after_print_cancelled_chime"
		elif script_name == "afterPrintDone":
			setting = "after_print_done_chime"
		elif script_name == "afterPrintPaused":
			setting = "after_print_paused_chime"
		elif script_name == "beforePrintResumed":
			setting = "before_print_resumed_chime"
		else:
			return (None, None)

		# Return if no chime set
		if self._settings.get([setting]) == "None":
			return (None, None)	

		print("Playing {0}".format(self._settings.get([setting])))

		# Get gcode from file
		with open('gcode/{0}.gcode'.format(self._settings.get([setting])), 'r') as file:
			chime = file.read()

		prefix = None
		postfix = chime

		return (prefix, postfix)

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Chimer"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = ChimerPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information, 
		"octoprint.comm.protocol.scripts": __plugin_implementation__.gcode_script_hook
	}

