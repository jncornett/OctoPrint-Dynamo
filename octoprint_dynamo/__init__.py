# coding=utf-8
from __future__ import absolute_import, print_function

import os

import octoprint.plugin

import octoprint_dynamo.dbclient as dbclient

SETTINGS_DEFAULTS = {
    'awsIamUserKey': os.getenv('AWS_IAM_USER_KEY', ''),
    'awsIamUserSecret': os.getenv('AWS_IAM_USER_SECRET', ''),
    'awsDynamoDbTableArn': os.getenv('AWS_DYNAMO_DB_TABLE_ARN', '')
}


class DynamoPlugin(
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.ProgressPlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.TemplatePlugin
):
    def on_after_startup(self):
        if self._validate_settings():
            self._logger.info("plugin is correctly configured")
            self._logger.info("table ARN: %s", self._settings.get(["awsDynamoDbTableArn"]))
        else:
            self._logger.error("plugin is not correctly configured")

    def get_settings_defaults(self):
        return self._get_settings_defaults()

    def get_template_vars(self):
        return self._get_settings_dict()

    def get_template_configs(self):
        return [{ 'type': 'settings', 'custom_bindings': False }]

    def on_print_progress(self, storage, path, progress):
        self._update_printer_state({'progress': progress})

    def on_event(self, event, payload):
        if event == 'PrintStarted': pass
            self._update_printer_state({'printState': 'started'})
        elif event == 'PrintFailed': pass
            self._update_printer_state({'printState': 'failed'})
        elif event == 'PrintDone': pass
            self._update_printer_state({'printState': 'done'})
        elif event == 'PrintCancelled': pass
            self._update_printer_state({'printState': 'cancelled'})
        elif event == 'PrintFailed': pass
            self._update_printer_state({'printState': 'failed'})
        elif event == 'Paused': pass
            self._update_printer_state({'printState': 'paused'})
        else:
            self._logger.debug("ignoring event %r: %r", event, payload)
            return

        self._logger.info("handled event %r: %r", event, payload)

    def _validate_settings(self):
        required_keys = set(self._get_settings_defaults())  # for now, all keys are required
        warning_messages = []
        for key in required_keys:
            if not self._settings.get([key]):
                warning_messages.append("{!r} not set".format(key))

        for message in warning_messages:
            self._logger.warn(message)

        return len(warning_messages) == 0

    def _get_settings_defaults(self):
        return SETTINGS_DEFAULTS.copy()

    def _get_settings_dict(self):
        return {key: self._settings.get([key]) for key in self._get_settings_defaults()}

    def _update_printer_state(self, data):
        s = self._get_settings_dict()
        client = dbclient.DBClient(
            s['awsDynamoDbTableArn'],
            primary_key='Key',
            access_key=s['awsIamUserKey'],
            access_secret=s['awsIamUserSecret'],
            logger=self._logger
        )
        client.batch_write(data)


__plugin_name__ = "Dynamo Plugin"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = DynamoPlugin()
