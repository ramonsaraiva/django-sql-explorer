from django.test import TestCase
from django.core.urlresolvers import reverse
from report.tests.factories import SimpleReportFactory
from report.models import Report
from django.contrib.auth.models import User
from django.forms.models import model_to_dict


class TestReportDetailView(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_report_with_bad_sql_renders_error(self):
        report = SimpleReportFactory(sql="error")
        resp = self.client.get(reverse("report_detail", kwargs={'report_id': report.id}))
        self.assertTemplateUsed(resp, 'report/report.html')

    def test_posting_report_saves_correctly(self):
        expected = 'select 2;'
        report = SimpleReportFactory(sql="select 1;")
        data = model_to_dict(report)
        data['sql'] = expected
        self.client.post(reverse("report_detail", kwargs={'report_id': report.id}), data)
        self.assertEqual(Report.objects.get(pk=report.id).sql, expected)

    def test_admin_required(self):
        self.client.logout()
        report = SimpleReportFactory(sql="before")
        resp = self.client.get(reverse("report_detail", kwargs={'report_id': report.id}))
        self.assertTemplateUsed(resp, 'admin/login.html')


class TestDownloadView(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_report_with_bad_sql_renders_error(self):
        report = SimpleReportFactory(sql="select 1;")
        resp = self.client.get(reverse("report_download", kwargs={'report_id': report.id}))
        self.assertEqual(resp['content-type'], 'text/csv')


class TestReportPlayground(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'pwd')
        self.client.login(username='admin', password='pwd')

    def test_empty_playground_renders(self):
        resp = self.client.get(reverse("report_playground"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'report/play.html')

    def test_playground_renders_with_prepopulated_sql(self):
        report = SimpleReportFactory(sql="select 1;")
        resp = self.client.get('%s?report_id=%s' % (reverse("report_playground"), report.id))
        self.assertTemplateUsed(resp, 'report/play.html')
        self.assertContains(resp, 'select 1;')

    def test_admin_required(self):
        self.client.logout()
        resp = self.client.get(reverse("report_playground"))
        self.assertTemplateUsed(resp, 'admin/login.html')