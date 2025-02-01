from rest_framework import serializers
from .models import User, Project, Task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']#şifreyi dönüştürmemek için.

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)  # Proje sahibini gösterelim read_only=true dediğimizde değiştirilemez sadece okunabilir demek istedik.
    members = UserSerializer(many=True, read_only=True)  # Proje üyelerini listeleyelim

    class Meta:
        model = Project
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)  #Atanan kullanıcı bilgisi read_only=true dediğimizde değiştirilemez sadece okunabilir demek istedik.
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())  #Proje id ile seçilecek

    class Meta:
        model = Task
        fields = '__all__' #Tüm alanları jsona çevir.
