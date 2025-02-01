from django.db import models


class User(models.Model):
    email=models.EmailField(unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.email


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True) # blank=true boş geçilebilir açıklama
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects'  # owner için farklı bir related_name
    )
    members = models.ManyToManyField( User, related_name='member_projects'  # members için farklı bir related_name
    )
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class Task(models.Model):
    task_name = models.CharField(max_length=200)
    task_description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    completed= models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')  #Task ataması.#eğer görev yoksa null=true olabilir görev varsa da blank=true ile boş geçilebilir
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()

    def __str__(self):
        return self.task_name #task_name'in string gösterimi düzgün görünmesi için.