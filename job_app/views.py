from decimal import Decimal
from multiprocessing import context
import profile
from unicodedata import category
from rest_framework.decorators import api_view
from youonline_social_app.custom_api_settings import CustomPagination
from . serializers import *
from youonline_social_app.serializers.users_serializers import *
from . models import *
from youonline_social_app.models import  UserWorkPlace
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from youonline_social_app.websockets.Constants import send_notifications_ws
from automotive_app.constants import is_valid_queryparam
from youonline_social_app.constants import s3_compress_image, upload_to_bucket, compress_saved_image
from youonline_social_app.youonline_threads import SendEmailThread


# Jobs Module
# Get All Industry API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_industries(request):
    industries = Industry.objects.all()
    serializer = IndustrySerializer(industries, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


# Get All Company API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_companies(request):
    companies = Company.objects.filter(is_deleted=False)
    serializer = GetCompanySerializer(companies, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
                    

# Create Company API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_company(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    name = request.data['name'] if 'name' in request.data else None
    logo = request.data['logo'] if 'logo' in request.data else None
    cover_image = request.data['cover_image'] if 'cover_image' in request.data else None
    license_file = request.data['license_file'] if 'license_file' in request.data else None
    email = request.data['email'] if 'email' in request.data else None
    phone = request.data['phone'] if 'phone' in request.data else None
    industry = request.data['industry'] if 'industry' in request.data else None
    country = request.data['country'] if 'country' in request.data else None
    state = request.data['state'] if 'state' in request.data else None
    city = request.data['city'] if 'city' in request.data else None
    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = str(profile.id)
    if not name or not logo or not email or not phone\
        or not industry or not country or not state or not city or not license_file:
        return Response({'success': False, 'response': {'message': "Invalid Data!"}},
                    status=status.HTTP_400_BAD_REQUEST)
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        company = serializer.save()
        try:
            # Compress the images
            if logo:
                new_image = compress_saved_image(company.logo.path)
                company.logo = new_image
                company.save()
            if cover_image:
                new_image = compress_saved_image(company.cover_image.path)
                company.cover_image = new_image
                company.save()
            # Upload to S3 Bucket
            if logo:
                upload_to_bucket(company.logo.path, company.logo.name)
                subprocess.call("rm " + company.logo.path, shell=True)
            if cover_image:
                upload_to_bucket(company.cover_image.path, company.cover_image.name)
                subprocess.call("rm " + company.cover_image.path, shell=True)
            if license_file:
                upload_to_bucket(company.license_file.path, company.license_file.name)
                subprocess.call("rm " + company.license_file.path, shell=True)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
        serializer=GetCompanySerializer(company)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


# Get My Company API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_company(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    industries = Company.objects.filter(profile=profile, is_deleted=False)
    serializer = GetCompanySerializer(industries, many=True)
    return Response({'status': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Update Company API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_company(request):
    id = request.data['id'] if 'id' in request.data else None
    logo = request.data['logo'] if 'logo' in request.data else None
    cover_image = request.data['cover_image'] if 'cover_image' in request.data else None
    license_file = request.data['license_file'] if 'license_file' in request.data else None
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        company = Company.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if company.profile != profile:
        return Response({'status': False, 'response': {'message': 'You are not authorized to update this company.'}},
                    status=status.HTTP_403_FORBIDDEN)
    serializer = CompanySerializer(company, data=request.data, partial=True)
    if serializer.is_valid():
        company=serializer.save()
        try:
            # Compress the images
            if logo:
                new_image = compress_saved_image(company.logo.path)
                company.logo = new_image
                company.save()
            if cover_image:
                new_image = compress_saved_image(company.cover_image.path)
                company.cover_image = new_image
                company.save()
            # Upload to S3 Bucket
            if logo:
                upload_to_bucket(company.logo.path, company.logo.name)
                subprocess.call("rm " + company.logo.path, shell=True)
            if cover_image:
                upload_to_bucket(company.cover_image.path, company.cover_image.name)
                subprocess.call("rm " + company.cover_image.path, shell=True)
            if license_file:
                upload_to_bucket(company.license_file.path, company.license_file.name)
                subprocess.call("rm " + company.license_file.path, shell=True)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
        serializer = GetCompanySerializer(company)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    return Response({'status': False, 'response': {'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST)


# Delete Company API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_company(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    id = request.query_params.get('id')
    try :
        company = Company.objects.get(id=id, is_deleted=False)
        if company.profile != profile:
            return Response({'success': False, 'response': {'message': 'You are not authorized to delete this company.'}},
                        status=status.HTTP_403_FORBIDDEN)
        company.is_deleted = True
        company.save()
        return Response({'success': True, 'response': {'message': 'Company deleted successfully'}},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

# # Get All Jobs API
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_all_jobs(request):
#     try:
#         profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
#     except Exception as e:
#         profile = None
#     try:
#         jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
#     except Exception as e:
#         jobprofile = None
#     jobs = Job.objects.filter(is_deleted=False).order_by("-created_at")
#     paginator = CustomPagination()
#     paginator.page_size = 9
#     result_page = paginator.paginate_queryset(jobs, request)
#     serializer = GetJobSerializer(result_page, many=True, context={"jobprofile":jobprofile})
#     return paginator.get_paginated_response(serializer.data)

# Update Job API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_job(request):
    id = request.data['id'] if 'id' in request.data else None
    try:
        created_by = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        job = Job.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = JobSerializer(job, data=request.data, partial=True)
    if serializer.is_valid():
        job = serializer.save()
        deleted_skills = request.data['deleted_skills'] if 'deleted_skills' in request.data else None
        added_skills = request.data['added_skills'] if 'added_skills' in request.data else None
        if deleted_skills:
            added_skills = added_skills[1:-1].replace('"', '').split(',')
            for i in deleted_skills:
                job.skill.remove(i)
        if added_skills:
            deleted_skills = deleted_skills[1:-1].replace('"', '').split(',')
            for i in added_skills:
                job.skill.add(i)
        serializer = GetJobSerializer(job)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def make_active_job(request):
    id = request.data.get('id', None)
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        job = Job.objects.get(id=id)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if job.is_active == True:
        job.is_active = False
        job.save()
        return Response({'success': True, 'response': {'message': 'Job inactive successfully!'}},
                status=status.HTTP_200_OK)
    else:
        job.is_active = True
        job.save()
        return Response({'success': True, 'response': {'message': 'Job active successfully!'}},
                status=status.HTTP_200_OK)

# Search Job API
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def search_jobs(request):
#     skill = request.query_params.get('skill')
#     location = request.query_params.get('location')
#     employment_type = request.query_params.get('employment_type')
#     salary_start_range = request.query_params.get('salary_start_range')
#     salary_end_range = request.query_params.get('salary_end_range')

#     try:
#         profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
#     except:
#         profile = None

#     try:
#         jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
#     except:
#         jobprofile = None

#     if not employment_type:
#         employment_type = ''

#     if not skill:
#         skill = ''

#     if not location:
#         location =''

#     if salary_start_range and salary_end_range:
#             job = Job.objects.filter(
#                                     Q(salary_start_range__gte=salary_start_range)& 
#                                     Q(salary_end_range__lte=salary_end_range)& 
#                                     Q(location__icontains=location)& 
#                                     Q(employment_type__icontains=employment_type)&
#                                     Q(skill__skill__icontains=skill), is_deleted=False)
#             for j in job:
#                 job_search_history = JobSearchHistory.objects.create(
#                                     jobprofile=jobprofile, 
#                                     salary_start_range=salary_start_range, 
#                                     salary_end_range=salary_end_range, 
#                                     location=location, 
#                                     employment_type=employment_type, 
#                                     skill=skill, job=j)

#     elif salary_start_range and not salary_end_range:
#             job = Job.objects.filter(
#                                     Q(salary_start_range__gte=salary_start_range)& 
#                                     Q(location__icontains=location)& 
#                                     Q(employment_type__icontains=employment_type)&
#                                     Q(skill__skill__icontains=skill
#                                     ) , is_deleted=False
#                                     )
#             for j in job:
#                 job_search_history = JobSearchHistory.objects.create(
#                                     jobprofile=jobprofile, 
#                                     salary_start_range=salary_start_range, 
#                                     location=location, 
#                                     employment_type=employment_type, 
#                                     skill=skill, job=j)
#     elif salary_end_range and not salary_start_range:
#             job = Job.objects.filter(
#                                     Q(salary_end_range__lte=salary_end_range)& 
#                                     Q(location__icontains=location)&                       
#                                     Q(employment_type__icontains=employment_type)&
#                                     Q(skill__skill__icontains=skill)
#                                     , is_deleted=False
#                                     )
#             for j in job:
#                 job_search_history = JobSearchHistory.objects.create(
#                                     jobprofile=jobprofile, 
#                                     salary_end_range=salary_end_range, 
#                                     location=location, 
#                                     employment_type=employment_type, 
#                                     skill=skill, job=j)

#     else:
#         job = Job.objects.filter(
#                                 Q(skill__skill__icontains=skill)&
#                                 Q(location__icontains=location) & 
#                                 Q(employment_type__icontains=employment_type) ,

#                                 is_deleted=False).distinct()
#         for j in job:
#             job_search_history = JobSearchHistory.objects.create(
#                                 jobprofile=jobprofile, 
#                                 location=location, 
#                                 employment_type=employment_type,
#                                 skill=skill, job=j)
#     serializer=GetJobSerializer(job, many=True, context={"jobprofile":jobprofile})
#     return Response({'success': True, 'response': {
#                 'message': serializer.data}
#                              }, status=status.HTTP_200_OK)


# Get Recent Job API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_recent_job(request):
    try:
        profile=Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile=None

    date_from = datetime.datetime.now() - datetime.timedelta(days=3)
    jobs = Job.objects.filter(created_at__gte=date_from, is_deleted=False).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    if profile:
        serializer = GetJobSerializer(result_page, many=True, context={"profile":profile})
    else:
        serializer = GetJobSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Apply Job API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_job(request):
    job = request.data['job'] if 'job' in request.data else None
    full_name = request.data['full_name'] if 'full_name' in request.data else None
    mobile =request.data['mobile'] if 'mobile' in request.data else None
    email = request.data['email'] if 'email' in request.data else None
    cover_letter = request.data['cover_letter'] if 'cover_letter' in request.data else None
    resume = request.data['resume'] if 'resume' in request.data else None
    dial_code = request.data['dial_code'] if 'dial_code' in request.data else None

    if not job or not full_name or not mobile or not email or not resume or not dial_code:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
        status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                     status=status.HTTP_404_NOT_FOUND)

    try:
        request.data._mutable = True
    except:
        pass
    request.data['profile'] = str(profile.id)


    serializer = JobApplySerializer(data=request.data)
    if serializer.is_valid():
        jobapply = serializer.save()
        serializer=GetJobApplySerializer(jobapply)
        return Response({'success': True, 'response':serializer.data},
                    status=status.HTTP_201_CREATED) 
    return Response({'success': False, 'response': {'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST)


# Create Job Profile APIs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job_profile(request):
    first_name = request.data['first_name'] if 'first_name' in request.data else None
    last_name = request.data['last_name'] if 'last_name' in request.data else None
    background_image = request.data['background_image'] if 'background_image' in request.data else None
    image = request.data['image'] if 'image' in request.data else None
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except  Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        request.data._mutable = True
        request.data['profile'] = profile.id
        if not first_name or not last_name:
            return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
        serializer = PostJobProfileSerializer(data=request.data)
        if serializer.is_valid():
            jobprofile = serializer.save()
            try:
                # Compress the images
                if image:
                    new_image = compress_saved_image(jobprofile.image.path)
                    jobprofile.image = new_image
                    jobprofile.save()
                if background_image:
                    new_image = compress_saved_image(jobprofile.background_image.path)
                    jobprofile.background_image = new_image
                    jobprofile.save()
                # Upload to S3 Bucket
                if image:
                    upload_to_bucket(jobprofile.image.path, jobprofile.image.name)
                    subprocess.call("rm " + jobprofile.image.path, shell=True)
                if background_image:
                    upload_to_bucket(jobprofile.background_image.path, jobprofile.background_image.name)
                    subprocess.call("rm " + jobprofile.background_image.path, shell=True)
            except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                            status=status.HTTP_400_BAD_REQUEST)
            serializer = GetJobProfileSerializer(jobprofile)
            return Response({'success': True, 'response': {
                'message': serializer.data}}, status=status.HTTP_201_CREATED)             
    return Response({'success': False, 'response': {
            'message': serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


# Update Job Profile
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_job_profile(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except  Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},status=status.HTTP_404_NOT_FOUND)
    background_image = request.data['background_image'] if 'background_image' in request.data else None
    image = request.data['image'] if 'image' in request.data else None
    try:
        jobprofile = JobProfile.objects.get(is_deleted=False, profile=profile)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    serializer = PostJobProfileSerializer(jobprofile, data=request.data, partial=True)
    if serializer.is_valid():
        jobprofile = serializer.save()
        try:
            # Compress the images
            if image:
                new_image = compress_saved_image(jobprofile.image.path)
                jobprofile.image = new_image
                jobprofile.save()
            if background_image:
                new_image = compress_saved_image(jobprofile.background_image.path)
                jobprofile.background_image = new_image
                jobprofile.save()
            # Upload to S3 Bucket
            if image:
                upload_to_bucket(jobprofile.image.path, jobprofile.image.name)
                subprocess.call("rm " + jobprofile.image.path, shell=True)
            if background_image:
                upload_to_bucket(jobprofile.background_image.path, jobprofile.background_image.name)
                subprocess.call("rm " + jobprofile.background_image.path, shell=True)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
        serializer = GetJobProfileSerializer(jobprofile)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


# Update Job Profile Skills
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_jobprofile_skills(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
        jobprofile = JobProfile.objects.get(profile=profile)
    except  Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    deleted_skills = request.data['deleted_skills'] if 'deleted_skills' in request.data else None
    added_skills = request.data['added_skills'] if 'added_skills' in request.data else None
    if deleted_skills:
        deleted_skills = deleted_skills[1:-1].replace('"', '').split(',')
        for i in deleted_skills:
            try:
                skill = Skill.objects.get(id=int(i))
                jobprofile.skill.remove(i)
            except Exception as e:
                print(e)
    if added_skills:
        added_skills = added_skills[1:-1].replace('"', '').split(',')
        for i in added_skills:
            try:
                skill = Skill.objects.get(id=int(i))
                jobprofile.skill.add(i)
            except Exception as e:
                print(e)
    jobprofile.save()
    return Response({"success": True, 'response': {'message': 'Skills updated successfully.'}},
                status=status.HTTP_200_OK)


# Get Job Profile API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_profile(request):
    username = request.query_params.get('username')
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None

    if username:
        try:
            job_profile = JobProfile.objects.get(
                profile__user__username=username, 
                is_deleted=False
            )
            serializer = GetJobProfileSerializer(job_profile, context={'jobprofile':job_profile})
            return Response(
                {
                    'success': True, 
                    'response': { 
                        'message': serializer.data
                    }
                }
                ,status=status.HTTP_200_OK
            )
        except JobProfile.DoesNotExist:
            return Response(
                {
                    "success": False,
                    'response': {
                        'message': 'Job Profile Does Not Exist'
                    }
                }
                ,status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "success": False, 
                    'response': {
                        'message': str(e)
                    }
                }
                ,status=status.HTTP_400_BAD_REQUEST
            )
    elif profile :
        try:
            job_profile = JobProfile.objects.get(
                profile=profile,
                is_deleted=False
            )
            serializer = GetJobProfileSerializer(job_profile, context={'jobprofile':job_profile})
            return Response(
                {
                    'success': True, 
                    'response': { 
                        'message': serializer.data
                    }
                }
                ,status=status.HTTP_200_OK
            )
        except JobProfile.DoesNotExist:
            return Response(
                {
                    "success": False,
                    'response': {
                        'message': 'Job Profile Does Not Exist'
                    }
                }
                ,status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "success": False, 
                    'response': {
                        'message': str(e)
                    }
                }
                ,status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            {
                'success': False, 
                'response': {
                    'message': 'Invalid Data!'
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

# Get Apply on Single Job API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_apply_single_job(request):
    job_id = request.query_params.get('job')
    if job_id:
        try:
            job = Job.objects.get(is_deleted=False, id=job_id)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)
        jobapply = JobApply.objects.filter(job=job)
        serializer = GetJobApplySerializer(jobapply, many=True)
        return Response({'success': True, 'response': {
            'message': serializer.data}
                         }, status=status.HTTP_200_OK)
    return Response({'success': False, 'response': {'message': serializer.errors}}
                            ,status=status.HTTP_400_BAD_REQUEST)


# Get My Jobs Apply API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_apply_on_jobs(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    apply_jobs = list(JobApply.objects.filter(profile=profile, is_deleted=False).values_list('job__id', flat=True))

    jobapply = Job.objects.filter(id__in=apply_jobs, is_deleted=False)
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobapply, request)
    serializer = GetJobSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Create Job Project API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job_project(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        name = request.data['name'] if 'name' in request.data else None
        description = request.data['description'] if 'description' in request.data else None
        image = request.data['image'] if 'image' in request.data else None
        video = request.data['video'] if 'video' in request.data else None
        request.data._mutable = True
        request.data['jobprofile'] = str(jobprofile.id)
        if not name or not description:
            return Response({'success': False, 'response': {
                'message': "Invalid Data!"}
                             }, status=status.HTTP_400_BAD_REQUEST)
        jobproject = JobProject.objects.create(
                        name=name, 
                        description=description, 
                        jobprofile=jobprofile
                    )
        if image:
            if len(request.FILES.getlist('image')) > 5:
                return Response({'success': False, 'response': {
                'message': "You can only upload 5 Images for one Project!"}
                             }, status=status.HTTP_400_BAD_REQUEST) 
            for img in request.FILES.getlist('image'):
                jobprojectmedia = JobProjectMedia(
                                    jobproject=jobproject,
                                    image=img
                                )
                jobprojectmedia.save()
        if video:
            for vid in request.FILES.getlist('video'):
                jobprojectmedia = JobProjectMedia(
                                    jobproject=jobproject,
                                    video=vid
                                )
                jobprojectmedia.save()
        serializer = GetJobProjectSerializer(jobproject)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


# Get Job Project API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_project(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    jobproject = JobProject.objects.filter(jobprofile=jobprofile, is_deleted=False)
    serializer = GetJobProjectSerializer(jobproject, many=True, context={"jobprofile":jobprofile})
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Get Single Job Project API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_single_job_project(request):
    id = request.query_params.get('id')
    try:
        jobproject = JobProject.objects.get(id=id, is_deleted=False)
        serializer = GetJobProjectSerializer(jobproject)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
                        

# Delete Job Project API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job_project(request):
    id=request.query_params.get('id')
    try:
        jobproject = JobProject.objects.get(id=id, is_deleted=False)
        jobproject.is_deleted=True
        jobproject.save()
        return Response({'success': True, 'response': {'message': 'Deleted Successfully!'}}, 
                    status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)                


# update Job Project API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_job_project(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_404_NOT_FOUND)
    try:
        jobproject = JobProject.objects.get(id=id, is_deleted=False)
        serializer = JobProjectSerializer(jobproject, data=request.data, partial=True)
        if request.method == 'PUT':
            if serializer.is_valid():
                jobproject=serializer.save()
                serializer=GetJobProjectSerializer(jobproject)
                return Response({'success': True, 'response': {'message': serializer.data}},
                            status=status.HTTP_201_CREATED)
            return Response({'status': False, 'response': {'message': serializer.errors}})
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)


# Similar Jobs API
@api_view(['GET'])
@permission_classes([AllowAny])
def similar_jobs(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED) 
    job = request.query_params.get('job')
    if not job:
        return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        job = Job.objects.get(id=job, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    skills = job.skill.all()
    similar_jobs = Job.objects.filter(skill__in=skills).distinct('id').exclude(id=job.id)
    serializer = GetJobSerializer(similar_jobs, many=True)
    return Response({"success": True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)


# Get Job Alert API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_alert(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND) 
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    

# Get Job Notification API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_notification(request):
    notifications = Notification.objects.filter(type='Job notification')
    serializer = GetJobNotificationSerializer(notifications, many=True)
    return Response({'success': True, 'response': {
                        'message': serializer.data,
                        'status': status.HTTP_200_OK}
                                     })


# Get Skill API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_skill(request):
    skills = Skill.objects.filter(is_deleted=False)
    serializer = GetSkillSerializer(skills, many=True)
    return Response({'success': True, 'response': {'message': serializer.data,
                                'status': status.HTTP_200_OK}
                                        })


# Create Job Story API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job_story(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    story_type = request.data['story_type'] if 'story_type' in request.data else 'Text'
    image = request.data['image'] if 'image' in request.data else None
    video = request.data['video'] if 'video' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    try:
        request.data._mutable = True
    except:
        pass
    request.data['jobprofile'] = str(jobprofile.id)
    if image:
        if image.size > 20971520:
            return Response({'success': False, 'response': {'message': "Please select a smaller image. Maximum allowed size is 20mb."}},
                    status=status.HTTP_400_BAD_REQUEST)
    if story_type == 'Media' and not video and not image:
        return Response({'success': False, 'response': {'message': 'Invalid Data.'}},
                    status=status.HTTP_400_BAD_REQUEST)
    serializer = JobStorySerializer(data=request.data)
    if serializer.is_valid():
        story = serializer.save()
        post = Post.objects.create(
                profile=story.jobprofile.profile,
                privacy=story.privacy,
                text=story.text,
                story_post=True,
            )
        story.post = post
        story.save()
        serializer = GetSingleJobStorySerializer(story)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


# Delete Job Story API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job_story(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED) 
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND) 
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        story = JobStory.objects.get(id=id, jobprofile = jobprofile, is_deleted=False)
    except:
        return Response({'success': False, 'response': {'message': 'Story does not exist. Or you are not authorized to delete it.'}},
                    status=status.HTTP_404_NOT_FOUND)
    post = story.post
    post.is_deleted = True
    post.save()
    story.is_deleted=True
    story.save()
    return Response({'success': True, 'response': {'message': 'Story deleted successfully.'}},
            status=status.HTTP_200_OK)


# Create Story View API
@api_view(['POST'])
@permission_classes([AllowAny])
def create_story_view(request):
    profile = request.data['profile'] if 'profile' in request.data else None
    story = request.data['story'] if 'story' in request.data else None
    if not profile or not story:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            story = ProfileStory.objects.get(id=story, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'Story does not exist.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = Profile.objects.get(id=profile, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'Profile does not exist.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST)
        if profile != story.profile:
            try:
                story_view = StoryView.objects.get(
                            story=story,
                            profile=profile,
                        )
                return Response({'success': True, 'response': {'message': 'Already viewed.'}},
                        status=status.HTTP_201_CREATED)
            except:
                story_view = StoryView.objects.create(
                            story=story,
                            profile=profile,
                        )
                return Response({'success': True, 'response': {'message': 'Viewed'}},
                        status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': 'Cannot add view for your own story.'}},
                    status=status.HTTP_400_BAD_REQUEST)


# Get All Job Profile Story API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_job_profile_stories(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    stories = JobStory.objects.filter(jobprofile=jobprofile, is_deleted=False).order_by("-created_at")
    serializer = GetSingleJobStorySerializer(stories, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
            status=status.HTTP_200_OK)


# Get All Job Story 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_stories(request):
    profile_id = request.query_params.get('profile_id')
    if not profile_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            profile = Profile.objects.get(id=profile_id, is_deleted=False)
        except ObjectDoesNotExist:
            return Response({'success': False, 'response': {'message': 'User Profile does not exist.'}},
                        status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({'success': False, 'response': {'message': 'Invalid Profile ID!'}},
                    status=status.HTTP_400_BAD_REQUEST)        
        stories = []
        try:
            story = ProfileStory.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')[0]
            story = GetSingleProfileStorySerializer(story).data
            stories.append(story)
        except Exception as e:
            pass
        try:
            following_list = FriendsList.objects.filter(profile=profile)[0].following.all()
            for i in following_list:
                try:
                    story = ProfileStory.objects.filter(profile=i, is_deleted=False).order_by('-created_at')[0]
                    story = GetSingleProfileStorySerializer(story).data
                    stories.append(story)
                except:
                    pass
        except Exception as e:
            pass
        # Sorting the given stories in a reverse order.
        stories = sorted(stories, key=lambda i: i['created_at'], reverse=True)
        return Response({'success': True, 'response': {'message': stories}},
                status=status.HTTP_200_OK)


# Add Job Endoresement API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_job_endoresements(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND) 
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        profile2 = request.data['profile2'] if 'profile2' in request.data else None
        text = request.data['text'] if 'text' in request.data else None
        skill = request.data['skill'] if 'skill' in request.data else None
        try:
            request.data._mutable = True
        except:
            pass
        if not jobprofile or not profile2 or not text or not skill:
            return Response({'success': False, 'response': {
                'message': "Invalid Data!" }
              
                             }, status=status.HTTP_400_BAD_REQUEST)
        request.data['profile1'] = str(jobprofile.id)
        serializer = JobEndoresementsSerializer(data=request.data)
        if serializer.is_valid():
            job_endoresement = serializer.save()
            serializer = GetJobEndoresementsSerializer(job_endoresement)
            return Response({'success': True, 'response': {'message': serializer.data}},
                        status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'response': {'message': serializer.errors}},
                        status=status.HTTP_400_BAD_REQUEST)


# Get Job Endoresement API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_endoresements(request):
    total_endoresements = JobEndoresements.objects.filter(is_deleted=False)
    serializer = GetJobEndoresementsSerializer(total_endoresements, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Delete Job Endoresement API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job_endoresements(request):
    id = request.data['id']
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND) 
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if id:
        try:
            job_endoresement = JobEndoresements.objects.get(id=id, profile1=jobprofile ,is_deleted=False)
            job_endoresement.is_deleted = True
            job_endoresement.save()
            return Response({'success': True, 'response': {
                'message': 'Deleted Successfully'}
                            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                                status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                                status=status.HTTP_400_BAD_REQUEST)


# Get Job Search History API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_search_history(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND) 
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    recent_search_job = JobSearchHistory.objects.filter(jobprofile=jobprofile).order_by('created_at')[:2]
    serializer = GetJobSearchHistorySerializer(recent_search_job, many=True, context={"jobprofile":jobprofile})
    return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_200_OK)


# Create Job Project Media API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job_project_media(request):
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND) 
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    jobproject = request.data['jobproject'] if 'jobproject' in request.data else None
    image = request.data['image'] if 'image' in request.data else None
    video = request.data['video'] if 'video' in request.data else None
    try:
        request.data._mutable = True
    except:
        pass
    request.data['jobprofile'] = str(jobprofile.id)
    serializer = JobProjectMediaSerializer(data=request.data)
    if serializer.is_valid():
        jobprojectmedia = serializer.save()
        serializer = GetJobProjectMediaSerialzer(jobprojectmedia)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


# Get Job Project Media API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_project_media(request):
    job_project_id = request.query_params.get('job_project_id')
    jobproject_media = JobProjectMedia.objects.filter(id =job_project_id, is_deleted=False)
    serializer = GetJobProjectMediaSerialzer(jobproject_media, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    

# Delete Job Project Media API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job_project_media(request):
    job_project_id = request.data['job_project_id'] if 'job_project_id' in request.data else None
    job_project_media = request.data['job_project_media'] if 'job_project_media' in request.data else None

    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND) 
    try:
        jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
                        
    if not job_project_id or not job_project_media:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        jobproject_media = JobProjectMedia.objects.get(
                                id=job_project_media,
                                jobproject=job_project_id, 
                                jobprofile=jobprofile, 
                                is_deleted=False)
        jobproject_media.is_deleted = True
        jobproject_media.save()
        return Response({'success': True, 'response': {'message': 'Deleted successfully'}},
                    status=status.HTTP_200_OK)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)   


################################################################################################################




@api_view(['GET'])
@permission_classes([AllowAny])
def search_jobs(request):
    # try:
    #     profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    # except:
    #     profile = None
    # try:
    #     jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
    # except:
    #     jobprofile = None

    # my_dict = dict()
    # if "location" in request.query_params !=None and "location" in request.query_params !='':
    #    my_dict["location__icontains"] = request.query_params.get('location')

    # if "job_type" in request.query_params !=None and "job_type" in request.query_params !='':
    #     my_dict["job_type__icontains"] = request.query_params.get('job_type')

    # if "salary_start_range" in request.query_params !=None and "salary_start_range" in request.query_params !='':
    #     my_dict["salary_start_range__gte"] = request.query_params.get('salary_start_range')

    # if "salary_end_range" in request.query_params !=None and "salary_end_range" in request.query_params !='':
    #     my_dict["salary_end_range__lte"] = request.query_params.get('salary_end_range')

    # job = ''
    # if is_valid_queryparam(my_dict):
    #     if len(my_dict) < 1:
    #         jobs = Job.objects.filter(is_deleted=False)
    #     else:
    #         jobs = Job.objects.filter(**my_dict, is_deleted=False).distinct()
    
    # if jobprofile:
    #     for j in jobs:
    #         if not j.jobsearchhistory_job.filter(jobprofile=jobprofile):
    #             search_history = JobSearchHistory.objects.create(
    #                                             jobprofile=jobprofile,
    #                                             job=j,
    #             )

    # paginator = CustomPagination()
    # paginator.page_size = 9
    # result_page = paginator.paginate_queryset(jobs, request)
    # serializer = GetJobSerializer(result_page, many=True)
    # return paginator.get_paginated_response(serializer.data)

    name = request.query_params.get('name') if 'name' in request.query_params else None
    category = request.query_params.get('category') if 'category' in request.query_params else None
    min_price = request.query_params.get('min_price') if 'min_price' in request.query_params else None
    max_price = request.query_params.get('max_price') if 'max_price' in request.query_params else None
    location = request.query_params.get('location') if 'location' in request.query_params else None

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None

    if not name:
        name = ''
    if not category:
        category = ''
    if not location:
        location = ''
    if category:
        try:
            category = JobCategory.objects.get(id=category)
            category.view_count += 1
            category.save()
            category = category.title
        except Exception as e:
                return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND
                )

    if min_price and max_price:
        jobs = Job.objects.filter(Q(title__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(location__icontains=location)&
                                        Q(salary_start__gte=min_price) &
                                        Q(salary_end__lte=max_price),
                                        is_deleted=False,
                                        is_active=True)
    elif min_price and not max_price:
        jobs = Job.objects.filter(Q(title__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(location__icontains=location)&
                                        Q(salary_start__gte=min_price),
                                        is_deleted=False,
                                        is_active=True)
    elif max_price and not min_price:
        jobs = Job.objects.filter(Q(title__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(location__icontains=location)&
                                        Q(salary_end__lte=max_price),
                                        is_deleted=False,
                                        is_active=True)
    else:
        jobs = Job.objects.filter(Q(title__icontains=name) &
                                        Q(category__title__icontains=category)&
                                        Q(location__icontains=location),
                                        is_deleted=False,
                                        is_active=True)
    if profile:
        for j in jobs:
            if not j.jobsearchhistory_job.filter(profile=profile):
                search_history = JobSearchHistory.objects.create(
                                                profile=profile,
                                                job=j,
                )

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    serializer = GetJobSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Add/Remove Favourite Job API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favourite_job(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)

    try:
        job = Job.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        try:
            favourite = FavoriteJob.objects.get(profile=profile, job=job)
            favourite.delete()
            return Response({'success': True, 'response': {'message': "Job removed from favourite List"}},
                            status=status.HTTP_200_OK)
        except:
            favourite = FavoriteJob.objects.create(profile=profile, job=job)
            return Response({'success': True, 'response': {'message': "Job added to favourite list"}},
                            status=status.HTTP_201_CREATED)




@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_categories(request):
    categories = JobCategory.objects.all()
    serializer = JobCategorySerializer(categories, many=True)
    return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_job_by_category(request):
    category = request.query_params['id'] if 'id' in request.query_params else None
    sorted_by = request.query_params['sorted_by'] if 'sorted_by' in request.query_params else None
    if not category:
        return Response ({"success": False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST) 
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None
        
    try:
        category = JobCategory.objects.get(id=category)
    except Exception as e:
        return Response ({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)   
                        
    if sorted_by == 'hightolow':
        jobs = Job.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-salary_start')

    elif sorted_by == 'lowtohigh':
        jobs = Job.objects.filter(category=category, is_deleted=False, is_active=True).order_by('salary_end')

    elif sorted_by == 'newtoold':
        jobs = Job.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        jobs = Job.objects.filter(category=category, is_deleted=False, is_active=True).order_by('created_at')

    elif sorted_by == 'featured':
        jobs = Job.objects.filter(category=category, is_deleted=False, is_promoted=True, is_active=True).order_by('-created_at')
    else:
        jobs = Job.objects.filter(category=category, is_deleted=False, is_active=True).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    if profile:
        serializer = GetJobSerializer(result_page, many=True, context={'profile': profile})
    else:
        serializer = GetJobSerializer(result_page, many=True)    
    return paginator.get_paginated_response(serializer.data)


# Recommended Job API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_job(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None

    if profile:
        search_history = JobSearchHistory.objects.filter(profile=profile)
    jobs = []
    if profile:
        if search_history:
            for h in search_history:
                job = Job.objects.filter(
                    id=h.job.id,
                    is_deleted=False,
                    is_active=True).distinct()
                if job:
                    for j in job:
                        jobs.append(j)
    else:
        date_from = datetime.datetime.now() - datetime.timedelta(days=3)
        jobs = Job.objects.filter(created_at__gte=date_from, is_deleted=False).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    if profile:
        serializer = GetJobSerializer(result_page, many=True, context={'profile':profile})
    else:
        serializer = GetJobSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Create Job API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    business_type = request.data['business_type'] if 'business_type' in request.data else None
    category = request.data['category'] if 'category' in request.data else None
    title = request.data['title'] if 'title' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    job_type = request.data['job_type'] if 'job_type' in request.data else None
    salary_start = request.data['salary_start'] if 'salary_start' in request.data else None
    salary_end = request.data['salary_end'] if 'salary_end' in request.data else None
    salary_period = request.data['salary_period'] if 'salary_period' in request.data else None
    position_type = request.data['position_type'] if 'position_type' in request.data else None
    location = request.data['location'] if 'location' in request.data else None
    longitude = request.data['longitude'] if 'longitude' in request.data else None
    latitude = request.data['latitude'] if 'latitude' in request.data else None
    salary_currency = request.data['salary_currency'] if 'salary_currency' in request.data else None 
    mobile = request.data['mobile'] if 'mobile' in request.data else None  
 
    dial_code = request.data['dial_code'] if 'dial_code' in request.data else None  
    salary_start = Decimal(salary_start)
    salary_end = Decimal(salary_end)

    if not title or not description  or not location or not category  or not dial_code\
        or not job_type or not salary_end or not salary_start or not salary_period  or not mobile\
            or not position_type or not longitude or not latitude or not salary_currency:
        return Response({'success': False, 'response': {'message': "Invalid Data!" }},
            status=status.HTTP_400_BAD_REQUEST)

    request.data._mutable = True
    request.data['profile'] = str(profile.id)
    serializer = JobSerializer(data=request.data)
    if serializer.is_valid():
        job = serializer.save()
        job.mobile = mobile
        job.is_active = True
        job.business_type = business_type
        if longitude or latitude:
            job.long = Decimal(longitude)
            job.lat = Decimal(latitude)
        job.save()

        # Email Send to ADMIN
        url = f'{settings.FRONTEND_SERVER_NAME}/admin/verification/job/' + str(job.id)
        html_template = render_to_string('email/u-job-email.html',
                                            {'id': str(job.slug),
                                            'url': url,
                                            'img_link': settings.DOMAIN_NAME,
                                            })
        text_template = strip_tags(html_template)
        subject = 'YouOnline | Job Verification'
        SendEmailThread(request, subject, html_template).start()

        # Creating Notification for Job
        notification = Notification(
        type = 'Job',
        profile = profile,
        text = f'Your job {job.title} is created successfully.',
        )
        notification.save()
        notification.notifiers_list.add(profile)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass
        # End Notification
        # post = Post.objects.create(profile=profile, job_post=True)

        # if skill_list:
        #  # Get Skill list and make a list of it.

        #     skills = skill_list[1:-1].replace('"', '').split(',')
        #     skills = [int(i) for i in skills]
        #     for i in skills:
        #         try:
        #             skill = Skill.objects.get(id=int(i))
        #             job.skill.add(skill)
        #         except:
        #             pass
        # job.save()

        serializer = GetJobSerializer(job)
            # SEO Meta creation
        filename = 'CSVFiles/XML/jobs.xml'
        open_file = open(filename,"r")
        read_file = open_file.read()
        open_file.close()
        new_line = read_file.split("\n")
        last_line = "\n".join(new_line[:-1])
        open_file = open(filename,"w+")
        for i in range(len(last_line)):
            open_file.write(last_line[i])
        open_file.close()
        loc_tag = f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{job.slug}</loc>\n"
        lastmod_tag = f"<lastmod>{job.created_at}</lastmod>\n"
        priorty_tag = f"<priority>0.8</priority>\n</url>\n</urlset>"
        with open(filename, "a") as fileupdate:
            fileupdate.write(loc_tag)
            fileupdate.write(lastmod_tag)
            fileupdate.write(priorty_tag)
        # SEO Meta Close
        return Response({'success': True, 'response': serializer.data},
                    status=status.HTTP_201_CREATED)
    return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def filtering_job(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except:
        profile = None
    my_dict = dict()

    if "title" in request.query_params !=None and "title" in request.query_params !='':
        my_dict["title__icontains"] = request.query_params.get('title')

    if "created_at" in request.query_params !=None and "created_at" in request.query_params !='':
        if request.query_params.get('created_at'):
            # created_at = request.query_params.get('created_at')
            # year, month, day = created_at.split('-')
            # my_date=datetime.date(int(year), int(month), int(day))
            my_dict["created_at__gte"] = request.query_params.get('created_at')

    if "salary_start" in request.query_params !=None and "salary_start" in request.query_params !='':
        if request.query_params.get('salary_start'):
            my_dict["salary_start__gte"] = request.query_params.get('salary_start')

    if "salary_end" in request.query_params !=None and "salary_end" in request.query_params !='':
        if request.query_params.get('salary_end'):
            my_dict["salary_end__lte"] = request.query_params.get('salary_end')

    if "job_type" in request.query_params !=None and "job_type" in request.query_params !='':
        if request.query_params.get('job_type') != 'All':
            my_dict["job_type__icontains"] = request.query_params.get('job_type')

    if "position_type" in request.query_params !=None and "position_type" in request.query_params !='':
        if request.query_params.get('position_type') != 'All':
            my_dict["position_type__icontains"] = request.query_params.get('position_type')
    
    if "currency" in request.query_params !=None and "currency" in request.query_params !='':
        currency = request.query_params.get('currency')
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
            print(e)

        my_dict["salary_currency__name__icontains"] = currency
    
    if "category" in request.query_params !=None and "category" in request.query_params !='':
        category = request.query_params.get('category')
        try:
            category = JobCategory.objects.get(id=category)
        except Exception as e:
            print(e)

        my_dict["category__title__icontains"] = category

    jobs = ''
    if is_valid_queryparam(my_dict):
        if len(my_dict) < 1:
            jobs = Job.objects.filter(is_deleted=False, is_active=True)
        else:
            jobs = Job.objects.filter(**my_dict, is_deleted=False, is_active=True).distinct()

            if profile:
                for j in jobs:
                    if not j.jobsearchhistory_job.filter(profile=profile):
                        try:
                            search_history = JobSearchHistory.objects.get(
                                                        profile=profile,
                                                        job=j,
                        )
                        except:
                            search_history = JobSearchHistory.objects.create(
                                                            profile=profile,
                                                            job=j,
                            )
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    if profile:
        serializer = GetJobSerializer(result_page, many=True, context={'profile':profile})
    else:
        serializer = GetJobSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# get My Jobs API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_jobs(request):
    sorted_by = request.query_params.get('sorted_by', None)
    # business_type = request.query_params.get('business_type', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)

    # if not business_type:
    #     return Response({"success": False, 'response': {'message': 'invalid data!'}},
    #                     status=status.HTTP_400_BAD_REQUEST)
                        
    # if business_type == 'Company':
    #     if sorted_by == 'hightolow':
    #         jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('-salary_end')

    #     elif sorted_by == 'lowtohigh':
    #         jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('salary_start')

    #     elif sorted_by == 'newtoold':
    #         jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('-created_at')

    #     elif sorted_by == 'oldtonew':
    #         jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('created_at')

    #     elif sorted_by == 'featured':
    #         jobs = Job.objects.filter(profile=profile, is_promoted=True, is_deleted=False, business_type='Company').order_by('-created_at')

    #     elif sorted_by == 'active':
    #         jobs = Job.objects.filter(profile=profile, is_active=True, is_deleted=False, business_type='Company').order_by('-created_at')

    #     elif sorted_by == 'inactive':
    #         jobs = Job.objects.filter(profile=profile, is_active=False, is_deleted=False, business_type='Company').order_by('-created_at')
    #     else:
    #         jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Company').order_by('-created_at')

    # elif business_type == 'Individual':

        # if sorted_by == 'hightolow':
        #     jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('-salary_end')

        # elif sorted_by == 'lowtohigh':
        #     jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('salary_start')

        # elif sorted_by == 'newtoold':
        #     jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('-created_at')

        # elif sorted_by == 'oldtonew':
        #     jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('created_at')

        # elif sorted_by == 'featured':
        #     jobs = Job.objects.filter(profile=profile, is_promoted=True, is_deleted=False, business_type='Individual').order_by('-created_at')

        # elif sorted_by == 'active':
        #     jobs = Job.objects.filter(profile=profile, is_active=True, is_deleted=False, business_type='Individual').order_by('-created_at')

        # elif sorted_by == 'inactive':
        #     jobs = Job.objects.filter(profile=profile, is_active=False, is_deleted=False, business_type='Individual').order_by('-created_at')
        # else:
        #     jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type='Individual').order_by('-created_at')
    if sorted_by == 'hightolow':
        jobs = Job.objects.filter(profile=profile, is_deleted=False).order_by('-salary_end')

    elif sorted_by == 'lowtohigh':
        jobs = Job.objects.filter(profile=profile, is_deleted=False).order_by('salary_start')

    elif sorted_by == 'newtoold':
        jobs = Job.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        jobs = Job.objects.filter(profile=profile, is_deleted=False).order_by('created_at')

    elif sorted_by == 'featured':
        jobs = Job.objects.filter(profile=profile, is_promoted=True, is_deleted=False).order_by('-created_at')

    elif sorted_by == 'active':
        jobs = Job.objects.filter(profile=profile, is_active=True, is_deleted=False).order_by('-created_at')

    elif sorted_by == 'inactive':
        jobs = Job.objects.filter(profile=profile, is_active=False, is_deleted=False).order_by('-created_at')
    else:
        jobs = Job.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    serializer = GetJobSerializer(result_page, many=True , context={"profile" : profile})
    return paginator.get_paginated_response(serializer.data)


# Get Single Job API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_job(request):
    job = request.query_params.get('job', None)
    try:
        profile = Profile.objects.get(
                            user=request.user, 
                            user__is_active=True, 
                            is_deleted=False)
    except:
        profile = None

    if not job:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        job = Job.objects.get(slug=job, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    if profile and profile != job.profile:
        job.view_count += 1
        job.save()

    # if profile or property.business_type == 'Company':
        # Creating Notification for Job 
        notification = Notification(
        type = 'Job',
        profile = profile,
        job_id=job.id,
        text = f'{profile.user.first_name} has viewed your ad',
        )
        notification.save()
        notification.notifiers_list.add(job.profile)
        notification.save()
        try:
            send_notifications_ws(notification)
        except:
            pass
        if job.view_count == 15:
            notification = Notification(
            type = 'Job',
            profile = profile,
            job_id=job.id,
            text = f'Your ad is getting more views and impressions. promote your ad or add special discounts to get customers.',
            )
            notification.save()
            notification.notifiers_list.add(job.profile)
            notification.save()
            try:
                send_notifications_ws(notification)
            except:
                pass
    if profile:
        serializer = GetJobSerializer(job, context={'profile':profile})
    else:
        serializer = GetJobSerializer(job)

    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)

# Delete Job API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                status=status.HTTP_400_BAD_REQUEST)
        
    try:
        job = Job.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_404_NOT_FOUND)
    job.is_deleted = True
    job.save()
    return Response({'success': True, 'response': {'message': "Deleted Successfully"}},
                status=status.HTTP_200_OK)


# Get Favourite All Jobs API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorite_jobs(request):
    sorted_by = request.query_params.get('sorted_by', None)

    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if sorted_by == 'hightolow':
        jobs = Job.objects.filter(favoritejob_job__profile=profile, is_deleted=False, is_active=True).order_by('-salary_end')

    elif sorted_by == 'lowtohigh':
        jobs = Job.objects.filter(favoritejob_job__profile=profile, is_deleted=False, is_active=True).order_by('salary_start')

    elif sorted_by == 'newtoold':
        jobs = Job.objects.filter(favoritejob_job__profile=profile, is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        jobs = Job.objects.filter(favoritejob_job__profile=profile, is_deleted=False, is_active=True).order_by('created_at')

    elif sorted_by == 'featured':
        jobs = Job.objects.filter(favoritejob_job__profile=profile, is_promoted=True, is_deleted=False, is_active=True).order_by('-created_at')

    else:
        jobs = Job.objects.filter(favoritejob_job__profile=profile, is_deleted=False, is_active=True).order_by('-created_at')

    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    serializer = GetJobSerializer(result_page, many=True, context={'profile': profile})
    return paginator.get_paginated_response(serializer.data)


# Get  All Jobs API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_jobs(request):

    sorted_by = request.query_params.get('sorted_by', None)
    
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None
        
    # jobs = '' 
    # category = request.query_params.get('category', None)
    # if category:
    #     try:
    #         category = JobCategory.objects.get(id=category)
    #     except Exception as e:
    #         return Response({"success": False, 'response': {'message': str(e)}},
    #                         status=status.HTTP_404_NOT_FOUND)
    # if category:
    #     jobs = Job.objects.filter(category__title__icontains=category.title, is_deleted=False, is_active=True).order_by('-created_at')
    # else:
    if sorted_by == 'hightolow':
        jobs = Job.objects.filter(is_deleted=False, is_active=True).order_by('-salary_end')

    elif sorted_by == 'lowtohigh':
        jobs = Job.objects.filter(is_deleted=False, is_active=True).order_by('salary_start')

    elif sorted_by == 'newtoold':
        jobs = Job.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')

    elif sorted_by == 'oldtonew':
        jobs = Job.objects.filter(is_deleted=False, is_active=True).order_by('created_at')

    elif sorted_by == 'featured':
        jobs = Job.objects.filter(is_deleted=False, is_promoted=True, is_active=True).order_by('-created_at')
    else:
        jobs = Job.objects.filter(is_deleted=False, is_active=True).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    if profile:
        serializer = GetJobSerializer(result_page, many=True, context={'profile': profile})
    else:
        serializer = GetJobSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# Get Featured Jobs API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_jobs(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        profile = None

    jobs = Job.objects.filter(is_promoted=True, is_deleted=False, verification_status='Verified').order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    if profile:
        serializer = GetJobSerializer(result_page, many=True, context={'profile': profile})
    else:
        serializer = GetJobSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def total_count_jobs(request):
    currency = request.query_params.get('currency', None)

    if currency:
        try:
            currency = Currency.objects.get(id=currency)
        except Exception as e:
            return Response({"success": False, 'response':{'message': str(e)}},
                                    status=status.HTTP_404_NOT_FOUND)


    first_count = ''
    second_count = ''
    third_count = ''
    fourth_count = ''
    fifth_count = ''
    first_value = ''
    second_value = ''
    third_value = ''
    fourth_value = ''
    fifth_value = ''
    sixth_value = ''
    if currency:
        if currency.code == 'AUD':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'CAD':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'KWD':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'AED':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'EUR':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'INR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'PKR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 500001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'GBP':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'CNH':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'OMR':
            first_value = 5000
            second_value = 10000
            third_value = 20000
            fourth_value = 30000
            fifth_value = 50000
            sixth_value = 50001

            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'UGX':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'ZAR':
            first_value = 50000
            second_value = 100000
            third_value = 200000
            fourth_value = 300000
            fifth_value = 500000
            sixth_value = 1500001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'CHF':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
        elif currency.code == 'USD':
            first_value = 1000
            second_value = 2000
            third_value = 5000
            fourth_value = 10000
            fifth_value = 15000
            sixth_value = 15001
            first_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=first_value, salary_end__lte=second_value).count()
            second_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=second_value, salary_end__lte=third_value).count()
            third_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=third_value, salary_end__lte=fourth_value).count()
            fourth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_start__gte=fourth_value, salary_end__lte=fifth_value).count()
            fifth_count = Job.objects.filter(is_deleted=False, verification_status='Verified', salary_currency__name__icontains=currency, salary_end__gte=sixth_value).count()
    
    data1 = {
        'first_value' : first_value,
        'second_value' : second_value,
        'total_count' : first_count,
    }
    data2 = {
        'first_value' : second_value,
        'second_value' : third_value,
        'total_count' : second_count,
    }

    data3 = {
        'first_value' : third_value,
        'second_value' : fourth_value,
        'total_count' : third_count,
    }

    data4 = {
        'first_value' : fourth_value,
        'second_value' : fifth_value,
        'total_count' : fourth_count,
    }

    data5 = {
        'second_value' : sixth_value,
        'total_count' : fifth_count
    }

    context = [data1, data2, data3, data4, data5]

    return Response({"success": True, 'response': context
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_job_media(request):
    job = request.data.get('job', None)
    job_image = request.data.getlist('job_image', None)
    job_video = request.data.get('job_video', None)


    if not job or (not job_image and not job_video):
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        job = Job.objects.get(id=job, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_400_BAD_REQUEST)
    if job_image:
        if job.jobmedia_job.filter(is_deleted=False).exclude(job_image=''):
            total_media = job.jobmedia_job.filter(is_deleted=False).exclude(job_image='').count()
            my_length = total_media + len(job_image)
            if my_length > 20:
                return Response({"success": False, 'response': {'message': 'Maximum 20 Image allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if len(job_image) > 20:
                return Response({"success": False, 'response': {'message': 'Maximum 20 Image allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
    if job_video:
        if job.jobmedia_job.filter(is_deleted=False).exclude(job_video=''):
            total_media = job.jobmedia_job.filter(is_deleted=False).exclude(job_video='').count()
            my_length = total_media + len(job_video)
            
            if my_length > 1:
                return Response({"success": False, 'response': {'message': 'Only One Video allowed!'}},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                if len(job_video) > 1:
                    return Response({"success": False, 'response': {'message': 'Only One Video allowed!'}},
                                    status=status.HTTP_400_BAD_REQUEST)

    if job_image:
        for a in job_image:
            media = JobMedia.objects.create(job=job, job_image=a, profile=profile)

    if job_video:
        media = JobMedia.objects.create(job=job, job_video=job_video, profile=profile)

    serializer = GetJobSerializer(job)
    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_resume(request):
    resume_file = request.data.get('resume_file', None)
    resume_name = request.data.get('resume_name', None)
    resume_extension = request.data.get('resume_extension', None)
    file_size = request.data.get('file_size', None)
    if not file_size:
        file_size = ''
        
    if not resume_file or not resume_name or not resume_extension:
        return Response({'success': False, 'response': {'message': "Invalid Data!"}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    
    media = JobApplyMedia.objects.create(profile=profile, resume_file=resume_file, resume_name=resume_name, resume_extension=resume_extension, file_size=file_size)
    serializer = JobApplyMediaSerializer(media)
    return Response({'success': True, 'response': serializer.data},
                        status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_resume(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    media = JobApplyMedia.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')
    serializer = JobApplyMediaSerializer(media, many=True)
    return Response({'success': True, 'response': serializer.data},
                            status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_resume(request):
    id = request.data.get('id', None)
    if not id:
        return Response({'success': False, 'response': {'message': "Invalid Data!"}},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        media = JobApplyMedia.objects.get(id=id)
        media.is_deleted = True
        media.save()
        return Response({'success': False, 'response': {'message': "Resume deleted successfuly"}},
                        status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': True, 'response': str(e)},
                                status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def near_job_ads(request):
    my_lat = request.query_params.get('lat')
    my_long = request.query_params.get('long')
    my_radius = request.query_params.get('radius')
    if my_lat or my_long:
        jobs = Job.objects.raw('SELECT *,  ( 6371 * acos( cos( radians('+my_lat+') ) * cos( radians( lat ) ) * cos( radians( long ) - radians('+my_long+') ) + sin( radians('+my_lat+') ) * sin( radians( lat ) ) ) ) AS distance FROM "Job" WHERE (6371 * acos( cos( radians('+my_lat+') ) * cos( radians(lat) ) * cos( radians(long) - radians('+my_long+') ) + sin( radians('+my_lat+') ) * sin( radians(lat) ) ) ) <= 100')
    else:
        jobs = Job.objects.filter(verification_status='Verified').order_by('-created_at')
    serializer = GetJobSerializer(jobs, many=True)

    return Response({"success": True, 'response': serializer.data
                                        }, status=status.HTTP_200_OK)


# get My Jobs API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_business_jobs(request):
    sorted_by = request.query_params.get('sorted_by', None)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)
    if sorted_by == 'hightolow':
        jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('-salary_end')

    elif sorted_by == 'lowtohigh':
        jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('salary_start')

    elif sorted_by == 'newtoold':
        jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('-created_at')

    elif sorted_by == 'oldtonew':
        jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('created_at')

    elif sorted_by == 'featured':
        jobs = Job.objects.filter(profile=profile, is_promoted=True, is_deleted=False, business_type="Company").order_by('-created_at')

    elif sorted_by == 'active':
        jobs = Job.objects.filter(profile=profile, is_active=True, is_deleted=False, business_type="Company").order_by('-created_at')

    elif sorted_by == 'inactive':
        jobs = Job.objects.filter(profile=profile, is_active=False, is_deleted=False, business_type="Company").order_by('-created_at')
    else:
        jobs = Job.objects.filter(profile=profile, is_deleted=False, business_type="Company").order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 8
    result_page = paginator.paginate_queryset(jobs, request)
    serializer = GetJobSerializer(result_page, many=True , context={"profile" : profile})
    return paginator.get_paginated_response(serializer.data)