import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import *
from App.controllers import *


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UnitTests(unittest.TestCase):
    #User Unit Tests
    def test_new_user(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"

    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='sha256')
        user = User("bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password(password)

    #Student Unit Tests
    def test_new_student(self):
      db.drop_all()
      db.create_all()
      student = Student("bob", "bobpass")
      assert student.username == "bob"

    def test_student_get_json(self):
      db.drop_all()
      db.create_all()
      student = Student("bob", "bobpass")
      self.assertDictEqual(student.get_json(), {"id": None, "username":"bob", "role": 'Student'})

    #Host Unit Tests
    def test_new_host(self):
      db.drop_all()
      db.create_all()
      host = Host("bill", "billpass", 101)
      assert host.username == "bill" and host.host_id == 101

    def test_host_get_json(self):
      db.drop_all()
      db.create_all()
      host = Host("bill", "billpass", 101)
      self.assertDictEqual(host.get_json(), {"id":None, "username":"bill", "role": 'Host', "host id": 101, "competitions": []})

    #Admin Unit Tests
    def test_new_admin(self):
      db.drop_all()
      db.create_all()
      admin = Admin("rob", "robpass", 1001)
      assert admin.username == "rob" and admin.staff_id == 1001

    def test_admin_get_json(self):
      db.drop_all()
      db.create_all()
      admin = Admin("rob", "robpass", 1001)
      self.assertDictEqual(admin.get_json(), {"id":None, "username":"rob", "role": 'Admin', "staff_id": 1001})

    #Competition Unit Tests
    def test_new_competition(self):
      db.drop_all()
      db.create_all()
      competition = Competition("RunTime")
      assert competition.name == "RunTime"

    def test_competition_get_json(self):
      db.drop_all()
      db.create_all()
      competition = Competition("RunTime")
      self.assertDictEqual(competition.get_json(), {"id": None,"name": "RunTime", "hosts": [], "participants": []})
      
    #Notification Unit Tests
    def test_new_notification(self):
      db.drop_all()
      db.create_all()
      notification = Notification(1, "Hello")
      assert notification.student_id == 1 and notification.message == "Hello"

    def test_notification_get_json(self):
      db.drop_all()
      db.create_all()
      notification = Notification(1, "Hello")
      self.assertDictEqual(notification.get_json(), {"id": None, "notification": "Hello"})
  
    #Ranking Unit Tests
    def test_new_ranking(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      assert ranking.student_id == 1
  
    def test_set_points(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      ranking.set_points(15)
      assert ranking.total_points == 15

    def test_set_ranking(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      ranking.set_ranking(1)
      assert ranking.curr_ranking == 1

    def test_previous_ranking(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      ranking.set_previous_ranking(1)
      assert ranking.prev_ranking == 1

    def test_ranking_get_json(self):
      db.drop_all()
      db.create_all()
      ranking = Ranking(1)
      ranking.set_points(15)
      ranking.set_ranking(1)
      self.assertDictEqual(ranking.get_json(), {"rank":1, "total points": 15})
    
    #CompetitionStudent Unit Tests
    def test_new_competition_student(self):
      db.drop_all()
      db.create_all()
      competition_student = CompetitionStudent(1, 1)
      assert competition_student.student_id == 1 and competition_student.comp_id == 1

    def test_competition_student_update_points(self):
      db.drop_all()
      db.create_all()
      competition_student = CompetitionStudent(1, 1)
      competition_student.update_points(15)
      assert competition_student.points_earned == 15

    def test_competition_student_get_json(self):
      db.drop_all()
      db.create_all()
      competition_student = CompetitionStudent(1, 1)
      competition_student.update_points(15)
      self.assertDictEqual(competition_student.get_json(), {"id": None, "student_id": 1, "competition_id": 1, "points_earned": 15})

    #CompetitionHost Unit Tests
    def test_new_competition_host(self):
      db.drop_all()
      db.create_all()
      competition_host = CompetitionHost(1, 1)
      assert competition_host.host_id == 1 and competition_host.comp_id == 1

    def test_competition_host_get_json(self):
      db.drop_all()
      db.create_all()
      competition_host = CompetitionHost(1, 1)
      self.assertDictEqual(competition_host.get_json(), {"id": None, "host_id": 1, "comp_id": 1})

'''
    Integration Tests
'''
class IntegrationTests(unittest.TestCase):
    
    #Feature 1 Integration Tests
    def test1_create_competition(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      assert comp.name == "RunTime"

    def test2_create_competition(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      assert create_competition("CodeSprint", 100) == None
      
    #Feature 2 Integration Tests
    def test1_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      student = create_student("bob", "bobpass")
      student_rank = create_ranking(student.id)
      register_student("bob", "RunTime")
      host = create_host("rob", "robpass", 1001)
      join_comp("rob", "RunTime")
      assert add_results("rob", "bob", "RunTime", 15) == True

    def test2_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      student = create_student("bob", "bobpass")
      student_rank = create_ranking(student.id)
      host = create_host("rob", "robpass", 1001)
      join_comp("rob", "RunTime")
      assert add_results("rob", "bob", "RunTime", 15) == False

    def test3_add_results(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      student = create_student("bob", "bobpass")
      student_rank = create_ranking(student.id)
      register_student("bob", "RunTime")
      host = create_host("rob", "robpass", 1001)
      assert add_results("rob", "bob", "RunTime", 15) == False

    #Feature 3 Integration Tests
    def test_display_student_info(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      student = create_student("bob", "bobpass")
      student_rank = create_ranking(student.id)
      register_student("bob", "RunTime")
      host = create_host("rob", "robpass", 1001)
      join_comp("rob", "RunTime")
      add_results("rob", "bob", "RunTime", 15)
      update_rankings()
      self.assertDictEqual(display_student_info("bob"), {"profile": {'id': 1, 'username': 'bob', 'role': 'Student'}, "ranking": {'rank': 1, 'total points': 15}, "participated_competitions": ['RunTime']})
      
    #Feature 4 Integration Tests
    def test_display_competition(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      student = create_student("bob", "bobpass")
      register_student("bob", "RunTime")
      host = create_host("rob", "robpass", 1001)
      join_comp("rob", "RunTime")
      self.assertDictEqual(comp.get_json(), {'id': 1, 'name': 'RunTime', 'hosts': ['rob'], 'participants': ['bob']})

    #Feature 5 Integration Tests
    def test_display_rankings(self):
      db.drop_all()
      db.create_all()
      bill = create_admin("bill", "billpass", 101)
      comp1 = create_competition('CodeSprint', 101)
      comp2 = create_competition('RunTime', 101)
      comp3 = create_competition('HashCode', 101)
      kim = create_host('kim', 'kimpass', 1000)
      join_comp(kim.username, 'CodeSprint')
      join_comp(kim.username, 'RunTime')
      rob = create_host('rob', 'robpass', 1001)
      join_comp(rob.username, 'RunTime')
      join_comp(rob.username, 'HashCode')
      ben = create_student('ben', 'benpass')
      ben_rank = create_ranking(ben.id)
      register_student('ben', 'CodeSprint')
      register_student('ben', 'RunTime')
      register_student('ben', 'HashCode')
      sally = create_student('sally', 'sallypass')
      sally_rank = create_ranking(sally.id)
      register_student('sally', 'CodeSprint')
      register_student('sally', 'RunTime')
      bob = create_student('bob', 'bobpass')
      bob_rank = create_ranking(bob.id)
      register_student('bob', 'RunTime')
      register_student('bob', 'HashCode')
      jake = create_student('jake', 'jakepass')
      jake_rank = create_ranking(jake.id)
      register_student('jake', 'CodeSprint')
      register_student('jake', 'HashCode')
      amy = create_student('amy', 'amypass')
      amy_rank = create_ranking(amy.id)
      register_student('amy', 'CodeSprint')
      jim = create_student('jim', 'jimpass')
      jim_rank = create_ranking(jim.id)
      register_student('jim', 'RunTime')
      add_results("rob", "ben", "RunTime", 10)
      add_results("kim", "ben", "CodeSprint", 10)
      add_results("rob", "ben", "HashCode", 10)
      add_results("kim", "sally", "RunTime", 15)
      add_results("kim", "sally", "CodeSprint", 15)
      add_results("rob", "bob", "RunTime", 15)
      add_results("rob", "bob", "HashCode", 10)
      add_results("kim", "jake", "CodeSprint", 10)
      add_results("rob", "jake", "HashCode", 10)
      add_results("kim", "amy", "CodeSprint", 20)
      add_results("rob", "jim", "RunTime", 15)
      update_rankings()
      self.assertListEqual(display_rankings(), [{"student": "ben", "ranking": {"rank": 1, "total points": 30}}, {"student": "sally", "ranking": {"rank": 1, "total points": 30}}, {"student": "bob", "ranking": {"rank": 3, "total points": 25}}, {"student": "jake", "ranking": {"rank": 4, "total points": 20}}, {"student": "amy", "ranking": {"rank": 4, "total points": 20}}, {"student": "jim", "ranking": {"rank": 6, "total points": 15}}])

    #Feature 6 Integration Tests
    def test1_display_notification(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      student = create_student("bob", "bobpass")
      student_rank = create_ranking(student.id)
      register_student("bob", "RunTime")
      host = create_host("rob", "robpass", 1001)
      join_comp("rob", "RunTime")
      add_results("rob", "bob", "RunTime", 15)
      update_rankings()
      self.assertDictEqual(display_notifications("bob"), {"notifications": [{"id": 1, "notification": "Ranking changed from Unranked to 1"}]})

    def test2_display_notification(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      host = create_host("rob", "robpass", 1001)
      join_comp("rob", "RunTime")
      ben = create_student("ben", "benpass")
      ben_rank = create_ranking(ben.id)
      register_student("ben", "RunTime")
      sally = create_student("sally", "sallypass")
      sally_rank = create_ranking(sally.id)
      register_student("sally", "RunTime")
      bob = create_student("bob", "bobpass")
      bob_rank = create_ranking(bob.id)
      register_student("bob", "RunTime")
      add_results("rob", "ben", "RunTime", 15)
      update_rankings()
      add_results("rob", "sally", "RunTime", 25)
      update_rankings()
      add_results("rob", "bob", "RunTime", 20)
      update_rankings()
      self.assertDictEqual(display_notifications("ben"), {"notifications": [{"id": 1, "notification": "Ranking changed from Unranked to 1"}, {"id": 5, "notification": "Ranking changed from 1 to 2"}, {"id": 8, "notification": "Ranking changed from 2 to 3"}]})

    #Additional Integration Tests
    def test_create_student(self):
      db.drop_all()
      db.create_all()
      student = create_student("bob", "bobpass")
      assert student.username == "bob"

    def test_create_host(self):
      db.drop_all()
      db.create_all()
      host = create_host("rob", "robpass", 101)
      assert host.username == "rob" and host.host_id == 101
  
    def test_create_admin(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 1001)
      assert admin.username == "bill" and admin.staff_id == 1001

    def test_student_list(self):
      db.drop_all()
      db.create_all()
      ben = create_student('ben', 'benpass')
      sally = create_student('sally', 'sallypass')
      bob = create_student('bob', 'bobpass')
      jake = create_student('jake', 'jakepass')
      amy = create_student('amy', 'amypass')
      students = get_all_students_json()
      
      self.assertEqual(students, [{'id': 1, 'username': 'ben', 'role': 'Student'}, {'id': 2, 'username': 'sally', 'role': 'Student'}, {'id': 3, 'username': 'bob', 'role': 'Student'}, {'id': 4, 'username': 'jake', 'role': 'Student'}, {'id': 5, 'username': 'amy', 'role': 'Student'}])

    def test_comp_list(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp1 = create_competition("CodeSprint", 101)
      comp2 = create_competition("RunTime", 101)
      comp3 = create_competition("HashCode", 101)
      comps = get_all_competitions_json()

      self.assertListEqual(comps, [{"id":1, "name":"CodeSprint", "hosts": [], "participants": []}, {"id":2, "name":"RunTime", "hosts": [], "participants": []}, {"id":3, "name":"HashCode", "hosts": [], "participants": []}])
    
    def test1_register_student(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      student = create_student("bob", "bobpass")
      assert register_student("bob", "RunTime") != None

    def test2_register_student(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      student = create_student("bob", "bobpass")
      register_student("bob", "RunTime")
      assert register_student("bob", "RunTime") == None
      
    def test1_join_comp(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      host = create_host("rob", "robpass", 1001)
      assert join_comp("rob", "RunTime") != None
       
    def test2_join_comp(self):
      db.drop_all()
      db.create_all()
      admin = create_admin("bill", "billpass", 101)
      comp = create_competition("RunTime", 101)
      host = create_host("rob", "robpass", 1001)
      join_comp("rob", "RunTime")
      assert join_comp("rob", "RunTime") == None
