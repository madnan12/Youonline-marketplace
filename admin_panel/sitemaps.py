from django.contrib.sitemaps import Sitemap
from classified_app.models import Classified
import xml.etree.ElementTree as ET

class ClassifiedsViewMap(Sitemap):
    
    priority = 0.8

    def items(self):
        return Classified.objects.filter(is_promoted=True, category__title__icontains='Electronic', is_deleted=False).select_related(
                    'category','sub_category','sub_sub_category','profile','post',
                    'company','country','state','city','language','currency'
                                                ).order_by('-created_at')


    def lastmod(self, obj):
        return obj.created_at
        
    