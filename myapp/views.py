
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, FileResponse
from django.views.decorators.csrf import csrf_exempt

import os
import json
import shutil

from zipfile import ZipFile

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize

PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]

usersJsonFile = os.path.join(os.path.dirname(__file__), 'users.json')
templateFile = os.path.join(os.path.dirname(__file__), 'template.txt')


@csrf_exempt
def get_users(request):
    if request.method == 'GET':
        with open(usersJsonFile, encoding="utf-8") as f:
            users = json.load(f)
        return JsonResponse(users, safe=False)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            user = json.loads(request.body)
            with open(usersJsonFile, 'r', encoding="utf-8") as f:
                data = json.load(f)
            user['id'] = max([u['id'] for u in data]) + 1
            data.append(user)
            with open(usersJsonFile, 'w', encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return JsonResponse(user, status=201)
        except json.JSONDecodeError:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def get_user(request, user_id):
    if request.method == 'GET':
        with open(usersJsonFile, encoding="utf-8") as f:
            users = json.load(f)
        for user in users:
            if user['id'] == int(user_id):
                return JsonResponse(user)
        return HttpResponseNotFound()
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def delete_user(request, user_id):
    if request.method == 'DELETE':
        with open(usersJsonFile, 'r', encoding="utf-8") as f:
            data = json.load(f)
        for i, user in enumerate(data):
            if user['id'] == int(user_id):
                data.pop(i)
                with open(usersJsonFile, 'w', encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                return JsonResponse({'message': 'User deleted'})
        return HttpResponseNotFound()
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def update_user(request, user_id):
    if request.method == 'PUT':
        try:
            user = json.loads(request.body)
            with open(usersJsonFile, 'r', encoding="utf-8") as f:
                data = json.load(f)
            for i, u in enumerate(data):
                if u['id'] == int(user_id):
                    data[i] = user
                    with open(usersJsonFile, 'w', encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                    return JsonResponse(user)
            return HttpResponseNotFound()
        except json.JSONDecodeError:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def create_and_download_texts(request):
    if request.method == 'GET':
        user_ids = request.GET.get('user_ids')
        if user_ids is None:
            return HttpResponseBadRequest()
        user_ids = [int(id) for id in user_ids.split(',')]
        files_dir = os.path.join(os.path.dirname(__file__), 'files')
        for filename in os.listdir(files_dir):
            file_path = os.path.join(files_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        with open(usersJsonFile, encoding="utf-8") as f:
            users = json.load(f)
        users = [user for user in users if user['id'] in user_ids]
        if not users:
            return HttpResponseNotFound()
        with open(templateFile, 'r', encoding="utf-8") as template:
            template_text = template.read()
        for user in users:
            user_file_text = template_text.format(**user)
            with open(f"{files_dir}/{user['name']} {user['last_name']}.txt", 'w', encoding="utf-8") as user_file:
                user_file.write(user_file_text)
        if len(users) == 1:
            file_path = f"{files_dir}/{users[0]['name']} {users[0]['last_name']}.txt"
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f"{users[0]['name']} {users[0]['last_name']}.txt")
        else:
            zipObj = ZipFile(f"{files_dir}/UserFiles.zip", 'w')
            for filename in os.listdir(files_dir):
                if filename.endswith(".txt"):
                    file_path = os.path.join(files_dir, filename)
                    zipObj.write(file_path, arcname=filename)
            zipObj.close()
            file_path = f"{files_dir}/UserFiles.zip"
            if os.path.exists(file_path):
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='UserFiles.zip')
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def create_and_download_pdfs(request):
    if request.method == 'GET':
        user_ids = request.GET.get('user_ids')
        if user_ids is None:
            return HttpResponseBadRequest()
        user_ids = [int(id) for id in user_ids.split(',')]
        files_dir = os.path.join(os.path.dirname(__file__), 'files')
        for filename in os.listdir(files_dir):
            file_path = os.path.join(files_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        with open(usersJsonFile, encoding="utf-8") as f:
            users = json.load(f)
        # Filter users based on the user IDs
        users = [user for user in users if user['id'] in user_ids]
        if not users:
            return HttpResponseNotFound()
        with open(templateFile, 'r', encoding="utf-8") as template:
            template_text = template.read()
        for user in users:
            user_file_text = template_text.format(**user)
            with open(f"{files_dir}/{user['name']} {user['last_name']}.txt", 'w', encoding="utf-8") as user_file:
                user_file.write(user_file_text)
        styles = getSampleStyleSheet()
        styleN = styles["BodyText"]
        for user in users:
            pdf_file_path = f"{files_dir}/{user['name']} {user['last_name']}.pdf"
            doc = SimpleDocTemplate(pdf_file_path, pagesize=letter)
            Story = []
            with open(f"{files_dir}/{user['name']} {user['last_name']}.txt", 'r', encoding='utf-8') as f:
                text_content = f.read()
                text_content = text_content.replace('\n', '<br/>')
                Story.append(Paragraph(text_content, styleN))
            doc.build(Story)
        if len(users) == 1:
            file_path = f"{files_dir}/{users[0]['name']} {users[0]['last_name']}.pdf"
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f"{users[0]['name']} {users[0]['last_name']}.pdf")
        else:
            zipObj = ZipFile(f"{files_dir}/UserFiles.zip", 'w')
            for filename in os.listdir(files_dir):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(files_dir, filename)
                    zipObj.write(file_path, arcname=filename)
            zipObj.close()
            file_path = f"{files_dir}/UserFiles.zip"
            if os.path.exists(file_path):
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='UserFiles.zip')
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def get_template(request):
    if request.method == 'GET':
        try:
            with open(templateFile, 'r', encoding="utf-8") as template:
                template_text = template.read()
            return JsonResponse({'template': template_text})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    else:
        return HttpResponseBadRequest()

@csrf_exempt
def update_template(request):
    if request.method == 'PUT':
        try:
            new_text = json.loads(request.body).get('new_text')
            if new_text is None:
                return HttpResponseBadRequest('Missing "new_text" in request body.')
            with open(templateFile, 'w', encoding="utf-8") as template:
                template.write(new_text)
            return JsonResponse({'message': 'Template updated successfully.'})
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON format.')
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    else:
        return HttpResponseBadRequest()