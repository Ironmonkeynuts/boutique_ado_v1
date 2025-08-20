from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    initial_text = _("Current Image")
    input_text = _("")
    clear_checkbox_label = _("Remove")
    template_name = (
        'products/custom_widget_templates/custom_clearable_file_input.html'
    )
