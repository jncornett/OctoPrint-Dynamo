# OctoPrint-Dynamo

This plugin listens to OctoPrint events and publishes changes in state to an AWS DynamoDB table.

The following OctoPrint events are handled:

- `PrintStarted`: set `printState` to `started`
- `PrintFailed`: set `printState` to `failed`
- `PrintDone`: set `printState` to `done`
- `PrintCancelled`: set `printState` to `cancelled`
- `PrintFailed`: set `printState` to `failed`
- `Paused`: set `printState` to `paused`

Additionally, the "print progress" event is handled and the plugin writes the
current progress to the `progress` record.

The key is written to the (configurable) primary key entry, and the value is written to the
(configurable) value entry.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/jncornett/OctoPrint-Dynamo/archive/master.zip

## Configuration

The following configuration options need to be set in order for the plugin to work properly:

- AWS Access Key
- AWS Access Secret
- AWS DynamoDB table ARN

The following configuration options are optional:

- Primary Key of the DynamoDB table (defaults to "Key")
- Value field of the DynamoDB table (defaults to "Value")

These options can be accessed through this plugins settings in the "OctoPrint Settings" modal.
