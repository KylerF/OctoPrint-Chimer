# coding=utf-8
from __future__ import absolute_import

import glob
import os

import octoprint.plugin

class ChimerPlugin(octoprint.plugin.SettingsPlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.TemplatePlugin):

	##~~ StartupPlugin mixin

	def on_after_startup(self):
		mute = self._settings.get_boolean(["mute"])
		self._logger.info("Chimer plugin started. muted = {mute}".format(**locals()))


	##~~ TemplatePlugin mixin

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	def get_template_vars(self):
		# Read all available GCODE chimes
		path = self._basefolder
		none_option = ["None"]
		avail_chimes = sorted(glob.glob("{path}/gcode/*.gcode".format(**locals())))
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
		# Software Update plugin configuration
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
		# Ignore non-gcode script events
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
			self._logger.error("Unrecognized action encountered: {script_name}".format(**locals()))
			return (None, None)

		# Return if no chime set
		if self._settings.get([setting]) == "None":
			return (None, None)	

		# Get gcode from file
		path = self._basefolder
		chime_name = self._settings.get([setting])
		with open('{path}/gcode/{chime_name}.gcode'.format(**locals()), 'r') as file:
			chime = file.read()

		prefix = None
		postfix = chime

		self._logger.debug("Playing {chime_name} in response to {script_name} event")

		return (prefix, postfix)


__plugin_name__ = "Chimer"
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
