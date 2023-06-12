from functools import partial
import profile
from unicodedata import category
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import  AllowAny
from youonline_social_app.constants import *
from youonline_social_app.decorators import *
from youonline_social_app.models import *
from . models import *
from . serializers import *
import datetime
from youonline_social_app.custom_api_settings import CustomPagination
from django.db.models import F

# Blog All Category  API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_blog_categories(request):
    Categories = BlogCategory.objects.all()
    serializer = BlogCategorySerializer(Categories, many=True)
    return Response({'success': True, 'response': {
        'message': serializer.data,
        'status': status.HTTP_200_OK},
                     }, status=status.HTTP_200_OK)

# Create Blog API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_blog(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    request.data._mutable = True
    request.data['profile'] = profile.id
    category = request.data['category'] if 'category' in request.data else None
    featured_image = request.data['featured_image'] if 'featured_image' in request.data else None
    title = request.data['title'] if 'title' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    tag = request.data['tags'] if 'tags' in request.data else None
    language = request.data['language'] if 'language' in request.data else None
    if not title or not category or not description or not language:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    serializer = BlogSerializer(data=request.data)
    if serializer.is_valid():
        blog = serializer.save()
        post = Post.objects.create(profile=profile, blog_post=True)
        blog.post = post
        blog.save()
        if featured_image:
            blog_media = BlogMedia(
                    blog = blog,
                    featured_image = featured_image,
                )
            blog_media.save()
        if tag:
            given_tags=tag[1:-1].replace('"', '').split(',')
            for t in given_tags:
                blogtags=BlogTag.objects.create(blog=blog, tags=t)
        serializer = GetBlogSerializer(blog)
        # SEO Meta Creation
        filename ='CSVFiles/XML/blogs.xml'
        open_file=open(filename,"r")
        read_file=open_file.read()
        open_file.close()
        new_line=read_file.split("\n")
        last_line="\n".join(new_line[:-1])
        open_file=open(filename,"w+")
        for i in range(len(last_line)):
            open_file.write(last_line[i])
        open_file.close()

        loc_tag=f"\n<url>\n<loc>{settings.FRONTEND_SERVER_NAME}/{blog.slug}</loc>\n"
        lastmod_tag=f"<lastmod>{blog.created_at}</lastmod>\n"
        priorty_tag=f"<priority>0.8</priority>\n</url>\n</urlset>"
        with open(filename, "a") as fileupdate:
            fileupdate.write(loc_tag)
            fileupdate.write(lastmod_tag)
            fileupdate.write(priorty_tag)
        # SEO Meta Close
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)

# Get All Blog API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_blogs(request):
    
    blogs = Blog.objects.filter(is_deleted=False).order_by('-created_at')
    serializer = GetBlogSerializer(blogs, many=True)
    return Response({'success': True, 'response': {
        'message': serializer.data,
        'status': status.HTTP_200_OK},
                     }, status=status.HTTP_200_OK)

# Get Single Blog
@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_blog(request):
    slug = request.query_params.get('slug')
    profile=None
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        pass
    try:
        blog = Blog.objects.get(slug=slug, is_deleted=False)
        blogwatched=BlogWatched.objects.create(profile=profile, blog=blog)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {
            'message': 'Blog does not exist',
            'status': status.HTTP_400_BAD_REQUEST}})

    serializer = GetBlogSerializer(blog)
    return Response({'success': True, 'response': {
        'message': serializer.data},
                        }, status=status.HTTP_200_OK)

# search blog by text
@api_view(['GET'])
@permission_classes([AllowAny])
def search_blogs(request):
    title= request.query_params.get('title')
    blogs=Blog.objects.filter(title__icontains=title, is_deleted=False)
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(blogs, request)
    serializer = GetBlogSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Get Latest Blog
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_blog(request):
    date_from = datetime.datetime.now() - datetime.timedelta(days=7)
    blogs=Blog.objects.filter(created_at__gte=date_from ,is_deleted=False).order_by('-created_at')
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(blogs, request)
    serializer = GetBlogSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Get My Blog API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_blogs(request):
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    blogs=Blog.objects.filter(is_deleted=False, profile=profile).order_by('-created_at')
    serializer=GetBlogSerializer(blogs, many=True)
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(blogs, request)
    serializer = GetBlogSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Create Blog Watch API
@api_view(['POST'])
@permission_classes([AllowAny])
def blog_add_to_watched(request):
    id=request.query_params.get('id')
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                    status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        pass
    try:
        blog = Blog.objects.get(id=id, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if profile != blog.profile:
        if profile:
            single_blog = Blog.objects.filter(id=id, is_deleted=False)
            single_blog.update(view_count = F('view_count') + 1)
            blogwatched=BlogWatched.objects.create(profile=profile, blog=blog)
        else:
            single_blog = Blog.objects.filter(id=id, is_deleted=False)
            single_blog.update(view_count = F('view_count') + 1)
            blogwatched=BlogWatched.objects.create(blog=blog)
        serializer=BlogWatchedSerializer(blogwatched)
        return Response({'success': True, 'response': {'message': 'Blog watched'}},
                       status=status.HTTP_201_CREATED)
    return Response({'success': True, 'response': {'message': 'Blog watched'}},
                        status=status.HTTP_201_CREATED)

# Trending Blog API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending_blogs(request):
    yesterday_time = datetime.datetime.now() - datetime.timedelta(days=1)
    blogs = Blog.objects.filter(
                            blogwatched_blog__created_at__gte=yesterday_time, 
                            is_deleted=False).order_by('-view_count').distinct()
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(blogs, request)
    serializer = GetBlogSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Add Featured Blog API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_featured_blog(request):
    slug=request.query_params.get('slug')
    try:
        blog=Blog.objects.get(is_deleted=False, slug=slug, is_promoted=False)
        blog.is_promoted=True
        blog.save()
        serializer=GetBlogSerializer(blog)
        return Response({'success': True, 'response': {
        'message': serializer.data,
        }}, status=status.HTTP_200_OK)
    except Exception as e:
		    return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)

# Get Featured Blog API
@api_view(['GET'])
@permission_classes([AllowAny])
def get_featured_blogs(request):
    blogs=Blog.objects.filter(is_deleted=False, is_promoted=True)
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(blogs, request)
    serializer = GetBlogSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# Delete Blog API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_blog(request):
    id=request.data['id'] if 'id' in request.data else None
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        blog=Blog.objects.get(is_deleted=False, id=id, profile=profile)
        blog.is_deleted=True
        blog.save()
        return Response({"success": True, 'response': {'message': 'Blog deleted successfully!'}},
				status=status.HTTP_200_OK)          
    except Exception as e:
		    return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)

# update Blog API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_blog(request):
    id = request.data['id'] if 'id' in request.data else None
    featured_image = request.data['featured_image'] if 'featured_image' in request.data else None
    if not id:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        blog=Blog.objects.get(is_deleted=False, id=id, profile=profile)
    except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
            status=status.HTTP_404_NOT_FOUND)
    serializer = BlogSerializer(blog, data=request.data, partial=True)
    if serializer.is_valid():
        blog = serializer.save()
        if featured_image:
            try:
                blog_media = BlogMedia.objects.get(
                        blog = blog,
                    )
                blog_media.delete()
            except Exception as e:
                pass
            blog_media = BlogMedia.objects.create(blog=blog, featured_image=featured_image)
            
        serializer = GetBlogSerializer(blog)
        return Response({'success': True, 'response': {'message': serializer.data}},
                    status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'response': {'message': serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST)
    

# Search Blog with Category
@api_view(['GET'])
@permission_classes([AllowAny])
def search_blog_by_category(request):
    category = request.query_params.get('category')
    if not category:
        return Response({'success':False, 'response': {'message':'Invalid Data!'}},
            status=status.HTTP_400_BAD_REQUEST)
    blogs = Blog.objects.filter(category=category, is_deleted=False)
    paginator = CustomPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(blogs, request)
    serializer = GetBlogSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def apply_blog_author(request):
    first_name = request.data['first_name'] if 'first_name' in request.data else None
    last_name = request.data['last_name'] if 'last_name' in request.data else None
    language = request.data['language'] if 'language' in request.data else None
    country = request.data['country'] if 'country' in request.data else None

    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    except Exception as e:
        return Response({"success": False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    if not first_name or not last_name or not language or not country:
        return Response({'success': False, 'response': {'message': 'Invalid Data!'}},
                status=status.HTTP_400_BAD_REQUEST)
    request.data._mutable = True
    request.data['profile'] = profile.id
    serializer = BlogAuthorSerializer(data=request.data)
    if serializer.is_valid():
        author = serializer.save()
        serializer = GetBlogAuthorSerializer(author)
        return Response({'success': True, 'response': {'message': serializer.data}},
                status=status.HTTP_201_CREATED)
    return Response({'success': False, 'response': {'message': serializer.errors}},
        status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_blog_author(request):
    author = BlogAuthor.objects.filter(is_deleted=False).order_by('-created_at')
    serializer = GetBlogAuthorSerializer(author, many=True)
    return Response({'success': True, 'response': {'message': serializer.data}},
            status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_blogs(request):
    date_from = datetime.datetime.now() - datetime.timedelta(days=7)
    yesterday_time = datetime.datetime.now() - datetime.timedelta(days=1)
    latest_blogs=Blog.objects.filter(created_at__gte=date_from ,is_deleted=False).order_by('-created_at')[:4]
    latest_blogs = GetBlogSerializer(latest_blogs, many=True).data
    trendy_blogs = Blog.objects.filter(
                            blogwatched_blog__created_at__gte=yesterday_time, 
                            is_deleted=False).order_by('-view_count').distinct()[:4]
    trendy_blogs = GetBlogSerializer(trendy_blogs, many=True).data
    featured_blogs=Blog.objects.filter(is_deleted=False, is_promoted=True)[:4]
    featured_blogs = GetBlogSerializer(featured_blogs, many=True).data
    results={
        'latest_blogs':latest_blogs,
        'trendy_blogs':trendy_blogs,
        'featured_blogs':featured_blogs,

    }
    return Response({'success': True, 'response': {'message': results},
                                    }, status=status.HTTP_200_OK)