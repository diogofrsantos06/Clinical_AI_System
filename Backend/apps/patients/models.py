from django.db import models

class Patient(models.Model):
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=255, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    numero_processo = models.CharField(max_length=50, null=True, blank=True)
    sexo = models.CharField(max_length=20, null=True, blank=True)
    nacionalidade = models.CharField(max_length=50, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    morada = models.TextField(null=True, blank=True)
    n_sns = models.CharField(max_length=50, null=True, blank=True)
    nif = models.CharField(max_length=20, null=True, blank=True)
    subsistema = models.CharField(max_length=100, null=True, blank=True)
    data_admissao = models.DateField(null=True, blank=True)
    servico = models.CharField(max_length=100, null=True, blank=True)
    medico = models.CharField(max_length=100, null=True, blank=True)
    contacto_urg_nome = models.CharField(max_length=100, null=True, blank=True)
    contacto_urg_telefone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} (Proc: {self.numero_processo})"