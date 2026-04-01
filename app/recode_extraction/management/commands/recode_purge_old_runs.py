from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from recode_extraction.models import SourceDocument, SourceExtractionRun


class Command(BaseCommand):
    help = 'Purge old RECODE extraction runs and optional orphaned source PDFs.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Delete runs finished before N days ago.')
        parser.add_argument('--dry-run', action='store_true', help='Only report what would be deleted.')
        parser.add_argument(
            '--delete-files',
            action='store_true',
            help='Also delete orphaned source document files (documents with no remaining runs).',
        )

    def handle(self, *args, **options):
        days = max(options['days'], 0)
        cutoff = timezone.now() - timedelta(days=days)
        dry_run = options['dry_run']
        delete_files = options['delete_files']

        old_runs = SourceExtractionRun.objects.filter(created_at__lt=cutoff)
        run_count = old_runs.count()
        source_ids = list(old_runs.values_list('source_id', flat=True).distinct())

        if dry_run:
            self.stdout.write(
                f'[dry-run] Would delete {run_count} run(s) created before {cutoff.isoformat()}.'
            )
        else:
            deleted, _ = old_runs.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted {run_count} run(s) created before {cutoff.isoformat()} (rows removed: {deleted}).'
                )
            )

        if delete_files and source_ids:
            orphaned = SourceDocument.objects.filter(id__in=source_ids, extraction_runs__isnull=True)
            file_count = 0
            source_count = orphaned.count()
            for source in orphaned:
                if source.pdf_file:
                    if dry_run:
                        file_count += 1
                    else:
                        source.pdf_file.delete(save=False)
                        file_count += 1
                if not dry_run:
                    source.delete()

            prefix = '[dry-run] ' if dry_run else ''
            self.stdout.write(
                f"{prefix}Orphaned source cleanup: sources={'would delete ' if dry_run else 'deleted '}{source_count}, "
                f"files={'would delete ' if dry_run else 'deleted '}{file_count}."
            )
