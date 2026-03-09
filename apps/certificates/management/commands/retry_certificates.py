"""
apps/certificates/management/commands/retry_certificates.py
Comando para reenviar certificados de inscrições com status 'pending'.
"""
from django.core.management.base import BaseCommand
from apps.registrations.models import Registration
from apps.certificates.tasks import issue_certificate_task


class Command(BaseCommand):
    help = "Reenvia certificados para todas as inscrições pendentes que possuem instrutor atribuído."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Tenta reenviar todos (mesmo sem instrutor - não recomendado)",
        )

    def handle(self, *args, **options):
        self.stdout.write("Buscando inscrições pendentes...")

        queryset = Registration.objects.filter(status=Registration.Status.PENDING)
        total_pending = queryset.count()

        if total_pending == 0:
            self.stdout.write(self.style.SUCCESS("Nenhuma inscrição pendente encontrada."))
            return

        # Filtra as que possuem instrutor, a menos que --all seja passado
        if not options["all"]:
            ready_to_send = queryset.filter(instructor__isnull=False)
            skipped = total_pending - ready_to_send.count()
        else:
            ready_to_send = queryset
            skipped = 0

        count = ready_to_send.count()

        if count == 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Encontradas {total_pending} inscrições, mas nenhuma possui instrutor atribuído. "
                    "Use o painel para atribuir um instrutor antes de tentar novamente."
                )
            )
            return

        self.stdout.write(f"Iniciando processamento de {count} inscrições...")
        if skipped > 0:
            self.stdout.write(self.style.NOTICE(f"Pulando {skipped} inscrições sem instrutor."))

        for reg in ready_to_send:
            issue_certificate_task.delay(str(reg.id))
            self.stdout.write(f"  - Enfileirado: {reg.full_name} ({reg.id})")

        self.stdout.write(
            self.style.SUCCESS(f"Sucesso! {count} tarefas de emissão foram enviadas para o Celery.")
        )
