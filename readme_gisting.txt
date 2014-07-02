Run Appraise
To run Appraise, install Django >= 1.3 and (optional) NLTK. In the project folder, run
$ manage.py runserver
which will launch a development server at 127.0.0.1:8000. The project comes with a pre-filled database (thus no need
to run syncdb) with some sample tasks and a superuser 'admin'.
A side note: although the original project requirements state Django >= 1.3, Django 1.4 - 1.6 did not work for me,
perhaps due to compatibility issues. I recommend using Django 1.3.5 for testing the toolkit.

User side
To use Appraise as an evaluator, go to http://127.0.0.1:8000/appraise/ and click the "Access your evaluation tasks"
button. Log in to the system (login: admin, password: admin), and you should see the list of available tasks. Click
on the task to start evaluation.

Admin side

Viewing and exporting task results
At http://127.0.0.1:8000/appraise/, click "Status" in the menu (black bar on top of the page). You will be taken to
a status page with all available tasks. Click a task to see detailed information on completion rate by user and to
access export to XML.

Adding new tasks to Appraise
To add new tasks, go to /appraise/admin/. Click the EvaluationTask objects link, then the button "Add EvaluationTask
object" in the upper right corner. In the page that opens, specify task name, task type (gisting) and upload the XML
file, which can be generated with gist_xml.py (see project folder 'eval'). Add task instructions ("Description") and
specify the users allowed to complete this task. Click "Save" button in the lower right corner when finished.