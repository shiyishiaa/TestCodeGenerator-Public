from typing import Dict

from PySide6.QtCore import Slot
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QDialog
from loguru import logger

from entity import ModelProvider, OpenAIModel, ClaudeModel, SiliconFlowModel, ModelSettings, MAX_TOKEN_MAP
from qmessagebox import failed_to_save, invalid_configuration, invalid_provider
from qwindow import SettingsModelUi
from util import read_model_settings, write_model_settings


class SettingsModel(QDialog, SettingsModelUi):
    MAX_TEMPERATURE = 2.0
    MIN_TEMPERATURE = 0.0
    TEMPERATURE_DECIMALS = 1
    TEMPERATURE_MULTIPLIER = 10

    PROVIDER_MODELS = {ModelProvider.Claude: ClaudeModel.__members__,
                       ModelProvider.SiliconFlow: SiliconFlowModel.__members__,
                       ModelProvider.OpenAI: OpenAIModel.__members__}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings = self.__read_settings()
        self.__setup_ui_components()
        self.__connect_signals()
        self.__load_data_to_ui()

    # ------------------------------------------------------------------------------------------------------------------

    def __read_settings(self) -> ModelSettings:
        """Read configuration."""
        try:
            return read_model_settings()
        except Exception as e:
            invalid_configuration(self, exception=e)
            return ModelSettings()

    def __write_settings(self) -> None:
        """Write configuration."""
        try:
            model_settings = self.settings
            model_settings.provider = ModelProvider(self.combo_box_model_provider.currentText())
            self.__update_provider_settings(model_settings.provider)
            model_settings.temperature = self.horizontal_slider_temperature.float_value
            write_model_settings(model_settings)
            logger.debug("Configuration saved successfully")
        except Exception as e:
            failed_to_save(self, message=f"Failed to save configuration: {e}")
            logger.error(f"Failed to save configuration: {e}")

    def __update_provider_settings(self, provider: ModelProvider) -> None:
        """Update provider-specific settings."""
        api_key = self.line_edit_api_key.text()
        api_host = self.line_edit_api_host.text()
        model_name = self.combo_box_model.currentText()

        provider_configs = {
            ModelProvider.Claude: {
                'api_key_attr': 'claude_api_key',
                'api_host_attr': 'claude_api_host',
                'model_attr': 'claude_model'
            },
            ModelProvider.SiliconFlow: {
                'api_key_attr': 'siliconflow_api_key',
                'api_host_attr': 'siliconflow_api_host',
                'model_attr': 'siliconflow_model'},
            ModelProvider.OpenAI: {
                'api_key_attr': 'openai_api_key',
                'api_host_attr': 'openai_api_host',
                'model_attr': 'openai_model'
            }
        }
        config = provider_configs.get(provider)
        if config:
            setattr(self.settings, config['api_key_attr'], api_key)
            setattr(self.settings, config['api_host_attr'], api_host)
            setattr(self.settings, config['model_attr'], model_name)

    def __setup_ui_components(self):
        self.combo_box_model_provider.addItems([p for p in ModelProvider])

        self.line_edit_temperature.setValidator(
            QDoubleValidator(self.MIN_TEMPERATURE, self.MAX_TEMPERATURE, self.TEMPERATURE_DECIMALS))

        self.horizontal_slider_temperature.multiplier = self.TEMPERATURE_MULTIPLIER

    # noinspection DuplicatedCode
    def __connect_signals(self):
        """Connect all signals to their slots."""
        # Connect provider and model signals
        self.combo_box_model_provider.currentTextChanged.connect(self.on_provider_changed)
        self.combo_box_model.currentTextChanged.connect(self.on_model_changed)

        # Connect temperature signals
        self.line_edit_temperature.editingFinished.connect(self.on_temperature_editing_finished)
        self.horizontal_slider_temperature.valueChangedFloat.connect(self.on_temperature_slider_changed)

        # Connect button signals
        self.button_box_confirm.accepted.connect(self.save_and_close)

    def __load_data_to_ui(self):
        """Load configuration data to UI components."""
        self.combo_box_model_provider.setCurrentText(self.settings.provider)
        self.combo_box_model_provider.currentTextChanged.emit(self.settings.provider)
        self.line_edit_temperature.setText(str(self.settings.temperature))
        self.horizontal_slider_temperature.float_value = self.settings.temperature

    def __get_provider_specific_settings(self, provider: ModelProvider) -> Dict[str, str]:
        """Get provider-specific settings."""
        provider_settings = {
            ModelProvider.Claude: {'api_key': self.settings.claude_api_key, 'api_host': self.settings.claude_api_host,
                                   'model': self.settings.claude_model if self.settings.claude_model else '',
                                   'models': self.PROVIDER_MODELS[ModelProvider.Claude].values()},
            ModelProvider.SiliconFlow: {'api_key': self.settings.siliconflow_api_key,
                                        'api_host': self.settings.siliconflow_api_host,
                                        'model': self.settings.siliconflow_model if self.settings.siliconflow_model else '',
                                        'models': self.PROVIDER_MODELS[ModelProvider.SiliconFlow].values()},
            ModelProvider.OpenAI: {'api_key': self.settings.openai_api_key, 'api_host': self.settings.openai_api_host,
                                   'model': self.settings.openai_model if self.settings.openai_model else '',
                                   'models': self.PROVIDER_MODELS[ModelProvider.OpenAI].values()}}
        return provider_settings.get(provider, provider_settings[ModelProvider.OpenAI])

    # ------------------------------------------------------------------------------------------------------------------

    @Slot(str)
    def on_provider_changed(self, text: str):
        """Handle provider change."""
        try:
            provider = ModelProvider(text)
            provider_settings = self.__get_provider_specific_settings(provider)

            self.line_edit_api_key.setText(provider_settings['api_key'])
            self.line_edit_api_host.setText(provider_settings['api_host'])

            self.combo_box_model.clear()
            self.combo_box_model.addItems(provider_settings['models'])
            if provider_settings['model']:
                self.combo_box_model.setCurrentText(provider_settings['model'])
        except Exception as e:
            invalid_provider(self, exception=e)
            logger.error(f"Error changing provider: {e}")

    @Slot(str)
    def on_model_changed(self, text: str):
        """Handle model change."""
        if text in MAX_TOKEN_MAP:
            self.label_max_token.setText(f"Max tokens: {MAX_TOKEN_MAP[text]}")
        else:
            self.label_max_token.setText("")

    @Slot()
    def on_temperature_editing_finished(self):
        """Handle temperature editing finished."""
        text = self.line_edit_temperature.text()

        try:
            value = float(text) if text else 0
            value = max(self.MIN_TEMPERATURE, min(self.MAX_TEMPERATURE, value))
            formatted_value = round(value, self.TEMPERATURE_DECIMALS)
            self.line_edit_temperature.setText(str(formatted_value))
            self.horizontal_slider_temperature.float_value = formatted_value
        except ValueError:
            current_value = self.horizontal_slider_temperature.float_value
            self.line_edit_temperature.setText(str(current_value))

    @Slot(float)
    def on_temperature_slider_changed(self, value: float):
        """Handle temperature slider changed."""
        self.line_edit_temperature.setText(str(value))

    @Slot()
    def save_and_close(self):
        """Save configuration and close dialog."""
        self.__write_settings()
        self.close()
