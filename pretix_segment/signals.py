import json
from collections import OrderedDict

import analytics
from django import forms
from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _

from pretix.base.settings import settings_hierarkey
from pretix.base.signals import (
    logentry_display, register_global_settings, register_payment_providers,
    requiredaction_display, order_placed, order_paid,
)
from pretix.control.signals import nav_organizer
from pretix.plugins.stripe.forms import StripeKeyValidator
from pretix.presale.signals import html_head


@receiver(register_global_settings, dispatch_uid='segment_global_settings')
def register_global_settings(sender, **kwargs):
    return OrderedDict([
        ('segment_api_key', forms.CharField(
            label=_('Segment API Key'),
            required=False,
        )),
    ])


@receiver(order_placed, dispatch_uid="segment_order_placed")
def order_placed(sender, **kwargs):
    order = kwargs['order']
    event = sender

    analytics.write_key = event.settings.get('segment_api_key')
    analytics.debug = True

    analytics.identify(order.email, {
        'email': order.email,
        'name': order.invoice_address.name
    })

    analytics.track(order.email, 'order_placed')


@receiver(order_paid, dispatch_uid='segment_order_paid')
def tracking_order_paid(sender, order, **kwargs):
    event = sender

    analytics.write_key = event.settings.get('segment_api_key')
    analytics.debug = True

    analytics.track(order.email, 'order_paid')

