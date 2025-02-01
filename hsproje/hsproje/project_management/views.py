from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
from .models import *
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


def user_list(request):
    users = User.objects.all()  # Tüm kullanıcıları alıyoruz
    user_data = []

    for user in users:
        user_data.append({
            'id': user.id,
            'email': user.email,
            'password': user.password  # Şifrenin plaintext hali burada olmasın, dikkat edin!
        })
    
    return JsonResponse(user_data, safe=False)  # safe=False kullanarak listeyi döndürebiliriz

@api_view(['POST'])  # POST isteğini kabul ediyoruz
def create_user(request):
    if request.method == 'POST':
        # Yeni kullanıcı için serializer kullanıyoruz
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():  # Verinin geçerli olup olmadığını kontrol ediyoruz
            # Kullanıcıyı kaydediyoruz
            serializer.save()
            return Response({'message': 'Kullanıcı başarıyla oluşturuldu!', 'user_id': serializer.data['id']}, status=201)
        return Response(serializer.errors, status=400)
    


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        # Email ile kullanıcıyı bulalım
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Geçersiz email veya şifre.'}, status=400)

    # Şifreyi düz metin olarak kontrol et
    if user.password == password:
        # JWT token oluşturma
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(refresh),
        })
    else:
        return Response({'error': 'Geçersiz email veya şifre.'}, status=400)


@api_view(['GET'])
def list_projects(request):
    """
    Tüm projeleri ve projeye ait kullanıcıları listelemek için fonksiyon.
    """
    projects = Project.objects.all()  # Tüm projeleri al
    serializer = ProjectSerializer(projects, many=True)  # Projeleri serialize et
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_project_details(request, project_id):
    """
    Belirli bir projeyi ve o projeye ait üyeleri listelemek için fonksiyon.
    """
    try:
        project = Project.objects.get(id=project_id)  # Projeyi ID ile bul
    except Project.DoesNotExist:
        return Response({'error': 'Proje bulunamadı!'}, status=status.HTTP_404_NOT_FOUND)

    # Projeye ait üyeleri (owner + members) alıyoruz
    project_data = ProjectSerializer(project).data
    members = project.members.all()  # Projeye ait üyeleri al
    members_serializer = UserSerializer(members, many=True)  # Üyeleri serialize et

    # Response olarak proje bilgisi ve üyeleri döndür
    project_data['members'] = members_serializer.data
    return Response(project_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Yalnızca giriş yapmış kullanıcılar proje oluşturabilir
def create_project(request):
    # Proje verilerini alıyoruz
    name = request.data.get('name')
    description = request.data.get('description', '')

    # Proje adı kontrolü
    if not name:
        return Response({'error': 'Proje adı gereklidir.'}, status=400)

    # Projeyi oluşturuyoruz ve giriş yapan kullanıcıyı owner olarak atıyoruz
    project = Project.objects.create(
        name=name,
        description=description,
        owner=request.user  # Giriş yapan kullanıcı proje sahibi olacak
    )

    # Projeyi JSON formatında döndürüyoruz
    serializer = ProjectSerializer(project)

    return Response({'message': 'Proje başarıyla oluşturuldu.', 'project': serializer.data}, status=201)


@api_view(['POST'])
def add_user_to_project(request, project_id):
    """
    E-posta adresi ile bir kullanıcıyı projeye eklemek için fonksiyon.
    """
    email = request.data.get('email')  # Kullanıcının e-posta adresini alıyoruz
    if not email:
        return Response({"error": "E-posta adresi belirtilmelidir!"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)  # Kullanıcıyı e-posta ile bul
    except User.DoesNotExist:
        return Response({"error": "Kullanıcı bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        project = Project.objects.get(id=project_id)  # Projeyi ID ile bul
    except Project.DoesNotExist:
        return Response({"error": "Proje bulunamadı!"}, status=status.HTTP_404_NOT_FOUND)

    # Kullanıcıyı projeye ekliyoruz
    project.members.add(user)
    project.save()

    return Response({"message": f"{email} başarıyla projeye eklendi!"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def task_list(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)