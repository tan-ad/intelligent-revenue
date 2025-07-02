import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from revenue_intelligence.analytics.models import Account
from revenue_intelligence.analytics.models import Contact
from revenue_intelligence.analytics.models import Opportunity


class Command(BaseCommand):
    help = "Loads data from CSV files into the database"

    @transaction.atomic
    def handle(self, *args, **options):
        # note: hard coded paths here, could consider putting into settings/.env
        # (but this is also the only place using this path so who cares)
        accounts_contacts_path = settings.BASE_DIR / "data/account_and_contact.csv"
        opportunities_path = settings.BASE_DIR / "data/opportunities.csv"

        self.stdout.write(self.style.SUCCESS("Starting data loading process..."))

        self.stdout.write("Deleting old data...")
        Opportunity.objects.all().delete()
        Contact.objects.all().delete()
        Account.objects.all().delete()

        df_ac = pd.read_csv(accounts_contacts_path)
        df_opp = pd.read_csv(opportunities_path)

        self.stdout.write("Processing accounts...")
        unique_accounts = df_ac[["Account ID", "Account Name"]].drop_duplicates(
            subset=["Account ID"],
        )
        for _, row in unique_accounts.iterrows():
            Account.objects.create(
                id=row["Account ID"],
                name=row["Account Name"],
            )
        self.stdout.write(
            self.style.SUCCESS(f"Processed {Account.objects.count()} accounts."),
        )

        self.stdout.write("Processing contacts...")
        for _, row in df_ac.iterrows():
            account_instance = Account.objects.get(id=row["Account ID"])
            Contact.objects.create(
                email=row["Email"],
                account=account_instance,
                first_name=row["First Name"],
                last_name=row["Last Name"],
                title=row["Title"],
            )
        self.stdout.write(
            self.style.SUCCESS(f"Processed {Contact.objects.count()} contacts."),
        )

        self.stdout.write("Processing opportunities...")
        for _, row in df_opp.iterrows():
            try:
                account_instance = Account.objects.get(id=row["Account ID"])
                contact_instance = None
                if pd.notna(row["Contact: Email"]):
                    contact_instance = Contact.objects.get(email=row["Contact: Email"])

                # Convert 'Probability (%)' to a decimal
                probability_decimal = row["Probability (%)"] / 100.0

                Opportunity.objects.create(
                    account=account_instance,
                    primary_contact=contact_instance,
                    name=row["Opportunity Name"],
                    stage=row["Stage"],
                    amount=row["Amount"],
                    probability=probability_decimal,
                    # Safely handle dates that might be in different formats or NaT
                    close_date=pd.to_datetime(row["Close Date"], errors="coerce").date()
                    if pd.notna(row["Close Date"])
                    else None,
                    created_date=pd.to_datetime(
                        row["Created Date"],
                        errors="coerce",
                    ).date()
                    if pd.notna(row["Created Date"])
                    else None,
                    next_step=row["Next Step"],
                    lead_source=row["Lead Source"],
                    opportunity_type=row["Type"],
                )
            except Account.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Account with id {row['Account ID']} not found. "
                        "Skipping opportunity.",
                    ),
                )
            except Contact.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Contact with email {row['Contact: Email']} not found. "
                        "Skipping contact link for opportunity.",
                    ),
                )
        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {Opportunity.objects.count()} opportunities.",
            ),
        )

        self.stdout.write(self.style.SUCCESS("Data loading complete!"))
