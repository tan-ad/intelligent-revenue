import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Account(models.Model):
    id = models.CharField(
        _("Account ID"), primary_key=True, max_length=255, editable=False
    )
    name = models.CharField(_("Account Name"), max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(models.Model):
    # Email is the most reliable unique identifier.
    email = models.EmailField(_("Email Address"), primary_key=True, max_length=255)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="contacts"
    )
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)
    title = models.CharField(_("Job Title"), max_length=255, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Opportunity(models.Model):
    class Stage(models.TextChoices):
        PROSPECTING = "Prospecting", _("Prospecting")
        QUALIFICATION = "Qualification", _("Qualification")
        PROPOSAL = "Proposal", _("Proposal")
        NEGOTIATION = "Negotiation", _("Negotiation")
        CLOSED_WON = "Closed Won", _("Closed Won")
        CLOSED_LOST = "Closed Lost", _("Closed Lost")

    # The CSV doesn't have a unique ID, so we use UUID.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="opportunities"
    )
    primary_contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )

    name = models.CharField(_("Opportunity Name"), max_length=255)
    stage = models.CharField(
        _("Stage"), max_length=50, choices=Stage.choices, default=Stage.PROSPECTING
    )
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=2)
    probability = models.DecimalField(
        _("Probability"),
        max_digits=3,
        decimal_places=2,
        help_text="A value between 0.00 and 1.00",
    )
    close_date = models.DateField(_("Close Date"), null=True, blank=True)
    created_date = models.DateField(_("Created Date"), null=True, blank=True)
    next_step = models.CharField(_("Next Step"), max_length=255, blank=True, null=True)
    lead_source = models.CharField(
        _("Lead Source"), max_length=100, blank=True, null=True
    )
    opportunity_type = models.CharField(
        _("Type"), max_length=100, blank=True, null=True
    )

    class Meta:
        ordering = ["-amount"]
        verbose_name_plural = "Opportunities"

    def __str__(self):
        return f"{self.name} for {self.account.name}"
