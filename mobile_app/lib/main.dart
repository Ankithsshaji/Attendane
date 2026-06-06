import 'dart:html' as html;
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:camera/camera.dart';

List<CameraDescription> cameras = [];

Future<void> main() async {

  WidgetsFlutterBinding.ensureInitialized();

  cameras = await availableCameras();

  runApp(const AttendanceApp());
}
class AttendanceApp extends StatelessWidget {
  const AttendanceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Attendance App',
      theme: ThemeData(useMaterial3: true),
      home: const RoleSelectionPage(),
    );
  }
}

class RoleSelectionPage extends StatelessWidget {
  const RoleSelectionPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),

      body: Center(
        child: Container(
          width: 420,
          margin: const EdgeInsets.all(24),
          padding: const EdgeInsets.all(30),

          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.08),
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: Colors.white10),
          ),

          child: Column(
            mainAxisSize: MainAxisSize.min,

            children: [

              const Icon(
                Icons.school_rounded,
                size: 80,
                color: Colors.white,
              ),

              const SizedBox(height: 20),

              const Text(
                'Attendance App',

                style: TextStyle(
                  color: Colors.white,
                  fontSize: 32,
                  fontWeight: FontWeight.w900,
                ),
              ),

              const SizedBox(height: 10),

              const Text(
                'Choose your login type',

                style: TextStyle(
                  color: Colors.white70,
                ),
              ),

              const SizedBox(height: 35),

              SizedBox(
                width: double.infinity,
                height: 55,

                child: ElevatedButton.icon(
                  icon: const Icon(Icons.person),

                  label: const Text('Student Login'),

                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const StudentLoginPage(),
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: 16),

              SizedBox(
                width: double.infinity,
                height: 55,

                child: ElevatedButton.icon(
                  icon: const Icon(Icons.badge),

                  label: const Text('Teacher Login'),

                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const TeacherLoginPage(),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class StudentLoginPage extends StatelessWidget {
  const StudentLoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const LoginDesign(
      title: 'Student Login',
      icon: Icons.person,
      color: Colors.green,
      apiUrl: 'http://127.0.0.1:8000/api/student-login/',
      dashboard: SizedBox(),
    );
  }
}

class TeacherLoginPage extends StatelessWidget {
  const TeacherLoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const LoginDesign(
      title: 'Teacher Login',
      icon: Icons.badge,
      color: Colors.deepPurple,
      apiUrl: 'http://127.0.0.1:8000/api/teacher-login/',
      dashboard: const SizedBox(),
    );
  }
}

class LoginDesign extends StatefulWidget {
  final String title;
  final IconData icon;
  final Color color;
  final String apiUrl;
  final Widget dashboard;

  const LoginDesign({
    super.key,
    required this.title,
    required this.icon,
    required this.color,
    required this.apiUrl,
    required this.dashboard,
  });

  @override
  State<LoginDesign> createState() => _LoginDesignState();
}

class _LoginDesignState extends State<LoginDesign> {

  final usernameController = TextEditingController();
  final passwordController = TextEditingController();

  bool loading = false;
  String error = '';

  Future<void> login() async {

    setState(() {
      loading = true;
      error = '';
    });

    try {

      final response = await http.post(
        Uri.parse(widget.apiUrl),

        headers: {
          'Content-Type': 'application/json',
        },

        body: jsonEncode({
          'username': usernameController.text.trim(),
          'password': passwordController.text.trim(),
        }),
      );

      final data = jsonDecode(response.body);

      if (data['success'] == true) {

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) {
              if (data['role'] == 'student') {
                return StudentDashboard(
                  username: data['username'],
                );
              } else {
                return TeacherDashboard(
                  username: data['username'],
                );
              }
            },
          ),
        );

      } else {

        setState(() {
          error = data['message'] ?? 'Login failed';
        });
      }

    } catch (e) {

      setState(() {
        error = 'Cannot connect to Django server';
      });
    }

    setState(() {
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: const Color(0xff0f172a),

      body: Center(
        child: SingleChildScrollView(

          padding: const EdgeInsets.all(24),

          child: Container(
            width: 420,
            padding: const EdgeInsets.all(30),

            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.08),
              borderRadius: BorderRadius.circular(30),
              border: Border.all(color: Colors.white10),
            ),

            child: Column(
              mainAxisSize: MainAxisSize.min,

              children: [

                Icon(
                  widget.icon,
                  size: 72,
                  color: widget.color,
                ),

                const SizedBox(height: 18),

                Text(
                  widget.title,

                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 30,
                    fontWeight: FontWeight.w900,
                  ),
                ),

                const SizedBox(height: 30),

                TextField(
                  controller: usernameController,

                  style: const TextStyle(color: Colors.white),

                  decoration: InputDecoration(
                    labelText: 'Username',

                    labelStyle: const TextStyle(
                      color: Colors.white70,
                    ),

                    prefixIcon: const Icon(
                      Icons.person,
                      color: Colors.white70,
                    ),

                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(18),

                      borderSide: const BorderSide(
                        color: Colors.white24,
                      ),
                    ),

                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(18),

                      borderSide: BorderSide(
                        color: widget.color,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 18),

                TextField(
                  controller: passwordController,
                  obscureText: true,

                  style: const TextStyle(color: Colors.white),

                  decoration: InputDecoration(
                    labelText: 'Password',

                    labelStyle: const TextStyle(
                      color: Colors.white70,
                    ),

                    prefixIcon: const Icon(
                      Icons.lock,
                      color: Colors.white70,
                    ),

                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(18),

                      borderSide: const BorderSide(
                        color: Colors.white24,
                      ),
                    ),

                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(18),

                      borderSide: BorderSide(
                        color: widget.color,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 12),

                if (error.isNotEmpty)
                  Text(
                    error,

                    style: const TextStyle(
                      color: Colors.redAccent,
                    ),
                  ),

                const SizedBox(height: 20),

                SizedBox(
                  width: double.infinity,
                  height: 54,

                  child: ElevatedButton(
                    onPressed: loading ? null : login,

                    style: ElevatedButton.styleFrom(
                      backgroundColor: widget.color,
                      foregroundColor: Colors.white,
                    ),

                    child: loading
                        ? const CircularProgressIndicator(
                            color: Colors.white,
                          )
                        : const Text(
                            'Login',
                            style: TextStyle(fontSize: 18),
                          ),
                  ),
                ),

                const SizedBox(height: 12),

                TextButton(
                  onPressed: () => Navigator.pop(context),

                  child: const Text(
                    'Back',

                    style: TextStyle(
                      color: Colors.white70,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class StudentDashboard extends StatefulWidget {
  final String username;

  const StudentDashboard({
    super.key,
    required this.username,
  });

  @override
  State<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends State<StudentDashboard> {
  String name = "";
  String registerNumber = "";
  double percentage = 0;

  int present = 0;
  int absent = 0;
  int late = 0;
  int total = 0;

  bool loading = true;

  Future<void> fetchStudentData() async {
    try {
      final response = await http.get(
        Uri.parse(
          'http://127.0.0.1:8000/api/student-dashboard/?username=${widget.username}',
        ),
      );

      final data = jsonDecode(response.body);

      if (data['success'] == true) {
        setState(() {

          name = data['name'];

          registerNumber =
              data['register_number'];

          percentage = double.parse(
            data['percentage'].toString(),
          );

          present = data['present'];

          absent = data['absent'];

          late = data['late'];

          total = data['total'];

          loading = false;
        });
      }
    } catch (e) {
      setState(() {
        loading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    fetchStudentData();
  }

  @override
  Widget build(BuildContext context) {
    return DashboardPage(
      title: loading ? 'Loading...' : name,
      subtitle: loading ? '' : 'Register No: $registerNumber',
      color: Colors.green,

      percentage: percentage,
      present: present,
      absent: absent,
      late: late,
      total: total,

      cards: [
        DashboardCard(
          icon: Icons.calendar_month,
          title: 'Timetable',
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => TimetablePage(
                  username: widget.username,
                ),
              ),
            );
          },
        ),
        DashboardCard(
          icon: Icons.history,
          title: 'Attendance History',
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => AttendanceHistoryPage(
                  username: widget.username,
                ),
              ),
            );
          },
        ),
        DashboardCard(
          icon: Icons.person,
          title: 'Profile',
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => StudentProfilePage(
                  username: widget.username,
                ),
              ),
            );
          },
        ),
        DashboardCard(
          icon: Icons.download,
          title: 'Download PDF',
          onTap: () {
            final url =
                'http://127.0.0.1:8000/api/student-attendance-pdf/?username=${widget.username}';

            html.window.open(url, '_blank');
          },
        ),
      ],
    );
  }
}
class TeacherDashboard extends StatelessWidget {
  final String username;

  const TeacherDashboard({
    super.key,
    required this.username,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),

      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),

          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(32),
                  gradient: const LinearGradient(
                    colors: [
                      Colors.deepPurple,
                      Colors.indigo,
                    ],
                  ),
                ),
                child: Row(
                  children: [
                    const CircleAvatar(
                      radius: 34,
                      backgroundColor: Colors.white24,
                      child: Icon(
                        Icons.badge,
                        color: Colors.white,
                        size: 38,
                      ),
                    ),

                    const SizedBox(width: 18),

                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Teacher Dashboard",
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 26,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            "Manage classes and attendance",
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                    ),

                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(
                        Icons.logout,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              Row(
                children: [
                  Expanded(
                    child: teacherStatCard(
                      "Students",
                      "View",
                      Icons.groups,
                      Colors.purpleAccent,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: teacherStatCard(
                      "Reports",
                      "Track",
                      Icons.bar_chart,
                      Colors.orangeAccent,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              const Text(
                "Quick Actions",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.w900,
                ),
              ),

              const SizedBox(height: 16),

              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisSpacing: 18,
                mainAxisSpacing: 18,
                childAspectRatio: 1.05,
                children: [

                  DashboardCard(
                    icon: Icons.face,
                    title: 'Face Attendance',
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => FaceRecognitionPage(
                          teacherUsername: username,
),
                        ),
                      );
                    },
                  ),
                  DashboardCard(
                    icon: Icons.calendar_month,
                    title: 'Timetable',
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => TeacherTimetablePage(
                            username: username,
                          ),
                        ),
                      );
                    },
                  ),
                  DashboardCard(
                    icon: Icons.groups,
                    title: 'Students List',
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const TeacherStudentsListPage(),
                        ),
                      );
                    },
                  ),

                  DashboardCard(
                    icon: Icons.bar_chart,
                    title: 'Attendance Report',
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const TeacherAttendanceReportPage(),
                        ),
                      );
                    },
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget teacherStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 34),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.w900,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
            ),
          ),
        ],
      ),
    );
  }
}

class DashboardPage extends StatelessWidget {

  final String title;
  final String? subtitle;

  final double percentage;

  final int present;
  final int absent;
  final int late;
  final int total;

  final Color color;
  final List<Widget> cards;

  const DashboardPage({
    super.key,
    required this.title,
    this.subtitle,

    this.percentage = 0,

    this.present = 0,
    this.absent = 0,
    this.late = 0,
    this.total = 0,

    required this.color,
    required this.cards,
  });
  
  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: const Color(0xff0f172a),

      body: SafeArea(
        child: SingleChildScrollView(

          padding: const EdgeInsets.all(20),

          child: Column(
            children: [

              Container(
                padding: const EdgeInsets.all(24),

                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(32),

                  gradient: LinearGradient(
                    colors: [
                      color,
                      color.withOpacity(0.55),
                    ],
                  ),
                ),

                child: Row(
                  children: [

                    const CircleAvatar(
                      radius: 34,
                      backgroundColor: Colors.white24,

                      child: Icon(
                        Icons.person,
                        color: Colors.white,
                        size: 38,
                      ),
                    ),

                    const SizedBox(width: 18),

                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,

                        children: [

                          Text(
                            title,

                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 28,
                              fontWeight: FontWeight.w900,
                            ),
                          ),

                          if (subtitle != null && subtitle!.isNotEmpty)

                            Text(
                              subtitle!,

                              style: const TextStyle(
                                color: Colors.white70,
                                fontSize: 15,
                              ),
                            ),
                        ],
                      ),
                    ),

                    IconButton(
                      onPressed: () => Navigator.pop(context),

                      icon: const Icon(
                        Icons.logout,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 26),

              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(28),

                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(30),
                  border: Border.all(color: Colors.white10),
                ),

                child: Column(
                  children: [

                    const Text(
                      'Attendance Percentage',

                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),

                    const SizedBox(height: 30),

                    SizedBox(
                      width: 180,
                      height: 180,

                      child: Stack(
                        alignment: Alignment.center,

                        children: [

                          SizedBox(
                            width: 180,
                            height: 180,
                            child: CircularProgressIndicator(
                              value: percentage / 100,
                              strokeWidth: 14,
                              backgroundColor: Colors.white12,
                              color: Colors.greenAccent,
                            ),
                          ),

                          Column(
                            mainAxisAlignment:
                                MainAxisAlignment.center,

                            children: [

                              Text(
                                '${percentage.toStringAsFixed(1)}%',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 42,
                                  fontWeight: FontWeight.w900,
                                ),
                              ),

                              Text(
                                '$present Present | $absent Absent',

                                style: TextStyle(
                                  color: Colors.white70,
                                  fontSize: 16,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 26),

              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),

                crossAxisSpacing: 18,
                mainAxisSpacing: 18,
                childAspectRatio: 1.05,

                children: cards,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class DashboardCard extends StatelessWidget {

  final IconData icon;
  final String title;
  final VoidCallback? onTap;

  const DashboardCard({
    super.key,
    required this.icon,
    required this.title,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {

    return InkWell(
      borderRadius: BorderRadius.circular(28),
      onTap: onTap,

      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(28),

          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,

            colors: [
              Colors.white.withOpacity(0.12),
              Colors.white.withOpacity(0.04),
            ],
          ),

          border: Border.all(color: Colors.white10),
        ),

        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,

          children: [

            Container(
              padding: const EdgeInsets.all(18),

              decoration: const BoxDecoration(
                shape: BoxShape.circle,

                gradient: LinearGradient(
                  colors: [
                    Colors.blue,
                    Colors.purple,
                  ],
                ),
              ),

              child: Icon(
                icon,
                color: Colors.white,
                size: 36,
              ),
            ),

            const SizedBox(height: 20),

            Text(
              title,
              textAlign: TextAlign.center,

              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class TimetablePage extends StatefulWidget {

  final String username;

  const TimetablePage({
    super.key,
    required this.username,
  });

  @override
  State<TimetablePage> createState() =>
      _TimetablePageState();
}

class _TimetablePageState
    extends State<TimetablePage> {

  List timetable = [];

  bool loading = true;

  Future<void> fetchTimetable() async {

    try {

      final response = await http.get(

        Uri.parse(

          'http://127.0.0.1:8000/api/student-timetable/?username=${widget.username}'

        ),
      );

      final data = jsonDecode(response.body);

      timetable = data['timetable'];

    } catch (e) {

      print(e);
    }

    setState(() {
      loading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    fetchTimetable();
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: const Color(0xff0f172a),

      appBar: AppBar(
        title: const Text("Timetable"),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: loading
    ? const Center(
        child: CircularProgressIndicator(),
      )
    : ListView.builder(
        padding: const EdgeInsets.all(18),
        itemCount: timetable.length,

        itemBuilder: (context, index) {

          final item = timetable[index];

          return Container(
            margin: const EdgeInsets.only(bottom: 18),
            padding: const EdgeInsets.all(18),

            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.08),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: Colors.white10),
            ),

            child: Column(
              crossAxisAlignment:
                  CrossAxisAlignment.start,

              children: [

                Text(
                  item['day'],

                  style: const TextStyle(
                    color: Colors.greenAccent,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 12),

                Text(
                  item['subject'],

                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 8),

                Text(
                  "${item['start_time']} - ${item['end_time']}",

                  style: const TextStyle(
                    color: Colors.white70,
                  ),
                ),

                const SizedBox(height: 6),

                Text(
                  "Teacher: ${item['teacher']}",

                  style: const TextStyle(
                    color: Colors.white70,
                  ),
                ),

                Text(
                  "Class: ${item['class_name']}",

                  style: const TextStyle(
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class AttendanceHistoryPage extends StatefulWidget {
  final String username;

  const AttendanceHistoryPage({
    super.key,
    required this.username,
  });

  @override
  State<AttendanceHistoryPage> createState() =>
      _AttendanceHistoryPageState();
}

class _AttendanceHistoryPageState
    extends State<AttendanceHistoryPage> {
  List attendance = [];
  bool loading = true;

  Future<void> fetchAttendanceHistory() async {
    try {
      final response = await http.get(
        Uri.parse(
          'http://127.0.0.1:8000/api/student-attendance-history/?username=${widget.username}',
        ),
      );

      final data = jsonDecode(response.body);

      if (data['success'] == true) {
        attendance = data['attendance'];
      }
    } catch (e) {
      print(e);
    }

    setState(() {
      loading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    fetchAttendanceHistory();
  }

  Color statusColor(String status) {
    if (status == 'Present') return Colors.greenAccent;
    if (status == 'Absent') return Colors.redAccent;
    if (status == 'Late') return Colors.orangeAccent;
    return Colors.white70;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),
      appBar: AppBar(
        title: const Text("Attendance History"),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : attendance.isEmpty
              ? const Center(
                  child: Text(
                    "No attendance found",
                    style: TextStyle(color: Colors.white70),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(18),
                  itemCount: attendance.length,
                  itemBuilder: (context, index) {
                    final item = attendance[index];

                    return Container(
                      margin: const EdgeInsets.only(bottom: 14),
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(22),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.event_available,
                            color: statusColor(item['status']),
                            size: 34,
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment:
                                  CrossAxisAlignment.start,
                              children: [
                                Text(
                                  item['subject'],
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 5),
                                Text(
                                  "${item['date']}  ${item['time']}",
                                  style: const TextStyle(
                                    color: Colors.white70,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Text(
                            item['status'],
                            style: TextStyle(
                              color: statusColor(item['status']),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}

class StudentProfilePage extends StatefulWidget {
  final String username;

  const StudentProfilePage({
    super.key,
    required this.username,
  });

  @override
  State<StudentProfilePage> createState() => _StudentProfilePageState();
}

class _StudentProfilePageState extends State<StudentProfilePage> {
  Map student = {};
  bool loading = true;

  Future<void> fetchProfile() async {
    final response = await http.get(
      Uri.parse(
        'http://127.0.0.1:8000/api/student-dashboard/?username=${widget.username}',
      ),
    );

    final data = jsonDecode(response.body);

    if (data['success'] == true) {
      setState(() {
        student = data;
        loading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    fetchProfile();
  }

  Widget infoTile(String title, String value, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.08),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.greenAccent),
          const SizedBox(width: 14),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(color: Colors.white70),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),
      appBar: AppBar(
        title: const Text("Student Profile"),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
body: loading
    ? const Center(child: CircularProgressIndicator())
    : ListView(
        padding: const EdgeInsets.all(18),
        children: [

          const CircleAvatar(
            radius: 46,
            backgroundColor: Colors.white24,
            child: Icon(
              Icons.person,
              color: Colors.white,
              size: 50,
            ),
          ),

          const SizedBox(height: 20),

          Center(
            child: Text(
              student['name'],
              style: const TextStyle(
                color: Colors.white,
                fontSize: 26,
                fontWeight: FontWeight.w900,
              ),
            ),
          ),

          const SizedBox(height: 25),

          infoTile(
            "Register No",
            student['register_number'],
            Icons.badge,
          ),

          infoTile(
            "Department",
            student['department'],
            Icons.school,
          ),

          infoTile(
            "Class",
            student['class_name'],
            Icons.class_,
          ),

          infoTile(
            "Total",
            student['total'].toString(),
            Icons.list,
          ),

          infoTile(
            "Present",
            student['present'].toString(),
            Icons.check_circle,
          ),

          infoTile(
            "Absent",
            student['absent'].toString(),
            Icons.cancel,
          ),

          infoTile(
            "Late",
            student['late'].toString(),
            Icons.access_time,
          ),

          infoTile(
            "Percentage",
            "${student['percentage']}%",
            Icons.percent,
          ),

          const SizedBox(height: 25),

          SizedBox(
            width: double.infinity,
            height: 55,

            child: ElevatedButton.icon(
              icon: const Icon(Icons.camera_alt),

              label: const Text(
                "Upload Face",
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),

              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
              ),

              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => LivelinessFaceUploadPage(
                      username: widget.username,
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class TeacherStudentsListPage extends StatefulWidget {
  const TeacherStudentsListPage({super.key});

  @override
  State<TeacherStudentsListPage> createState() =>
      _TeacherStudentsListPageState();
}

class _TeacherStudentsListPageState
    extends State<TeacherStudentsListPage> {
  List students = [];
  bool loading = true;

  Future<void> fetchStudents() async {
    try {
      final response = await http.get(
        Uri.parse(
          'http://127.0.0.1:8000/api/teacher-students-list/',
        ),
      );

      final data = jsonDecode(response.body);

      if (data['success'] == true) {
        students = data['students'];
      }
    } catch (e) {
      print(e);
    }

    setState(() {
      loading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    fetchStudents();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),
      appBar: AppBar(
        title: const Text("Students List"),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : students.isEmpty
              ? const Center(
                  child: Text(
                    "No students found",
                    style: TextStyle(color: Colors.white70),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(18),
                  itemCount: students.length,
                  itemBuilder: (context, index) {
                    final student = students[index];

                    return Container(
                      margin: const EdgeInsets.only(bottom: 14),
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(22),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: Row(
                        children: [
                          const CircleAvatar(
                            backgroundColor: Colors.white24,
                            child: Icon(
                              Icons.person,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment:
                                  CrossAxisAlignment.start,
                              children: [
                                Text(
                                  student['name'],
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 17,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  "Reg No: ${student['register_number']}",
                                  style: const TextStyle(
                                    color: Colors.white70,
                                  ),
                                ),
                                Text(
                                  "${student['department']} - ${student['class_name']}",
                                  style: const TextStyle(
                                    color: Colors.white70,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}

class TeacherMarkAttendancePage extends StatefulWidget {
  const TeacherMarkAttendancePage({super.key});

  @override
  State<TeacherMarkAttendancePage> createState() =>
      _TeacherMarkAttendancePageState();
}

class _TeacherMarkAttendancePageState
    extends State<TeacherMarkAttendancePage> {
  List students = [];
  List subjects = [];

  dynamic selectedStudent;
  dynamic selectedSubject;
  String selectedStatus = "Present";

  bool loading = true;
  bool saving = false;

  Future<void> fetchData() async {
    try {
      final studentResponse = await http.get(
        Uri.parse('http://127.0.0.1:8000/api/teacher-students-list/'),
      );

      final subjectResponse = await http.get(
        Uri.parse('http://127.0.0.1:8000/api/teacher-subjects/'),
      );

      final studentData = jsonDecode(studentResponse.body);
      final subjectData = jsonDecode(subjectResponse.body);

      if (studentData['success'] == true) {
        students = studentData['students'];
      }

      if (subjectData['success'] == true) {
        subjects = subjectData['subjects'];
      }
    } catch (e) {
      print(e);
    }

    setState(() {
      loading = false;
    });
  }

  Future<void> markAttendance() async {
    if (selectedStudent == null || selectedSubject == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Select student and subject"),
        ),
      );
      return;
    }

    setState(() {
      saving = true;
    });

    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/api/teacher-mark-attendance/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'student_id': selectedStudent['id'],
          'subject_id': selectedSubject['id'],
          'status': selectedStatus,
        }),
      );

      final data = jsonDecode(response.body);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(data['message'] ?? 'Done'),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Failed to mark attendance"),
        ),
      );
    }

    setState(() {
      saving = false;
    });
  }

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  InputDecoration dropdownStyle(String label) {
    return InputDecoration(
      labelText: label,
      labelStyle: const TextStyle(color: Colors.white70),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: Colors.white24),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: Colors.deepPurpleAccent),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),
      appBar: AppBar(
        title: const Text("Mark Attendance"),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  DropdownButtonFormField(
                    value: selectedStudent,
                    dropdownColor: const Color(0xff1e293b),
                    decoration: dropdownStyle("Select Student"),
                    items: students.map((student) {
                      return DropdownMenuItem(
                        value: student,
                        child: Text(
                          "${student['name']} - ${student['register_number']}",
                          style: const TextStyle(color: Colors.white),
                        ),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedStudent = value;
                      });
                    },
                  ),

                  const SizedBox(height: 18),

                  DropdownButtonFormField(
                    value: selectedSubject,
                    dropdownColor: const Color(0xff1e293b),
                    decoration: dropdownStyle("Select Subject"),
                    items: subjects.map((subject) {
                      return DropdownMenuItem(
                        value: subject,
                        child: Text(
                          subject['name'],
                          style: const TextStyle(color: Colors.white),
                        ),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedSubject = value;
                      });
                    },
                  ),

                  const SizedBox(height: 18),

                  DropdownButtonFormField<String>(
                    value: selectedStatus,
                    dropdownColor: const Color(0xff1e293b),
                    decoration: dropdownStyle("Status"),
                    items: const [
                      DropdownMenuItem(
                        value: "Present",
                        child: Text("Present", style: TextStyle(color: Colors.white)),
                      ),
                      DropdownMenuItem(
                        value: "Absent",
                        child: Text("Absent", style: TextStyle(color: Colors.white)),
                      ),
                      DropdownMenuItem(
                        value: "Late",
                        child: Text("Late", style: TextStyle(color: Colors.white)),
                      ),
                    ],
                    onChanged: (value) {
                      setState(() {
                        selectedStatus = value!;
                      });
                    },
                  ),

                  const SizedBox(height: 30),

                  SizedBox(
                    width: double.infinity,
                    height: 55,
                    child: ElevatedButton.icon(
                      onPressed: saving ? null : markAttendance,
                      icon: const Icon(Icons.check_circle),
                      label: Text(
                        saving ? "Saving..." : "Mark Attendance",
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.deepPurple,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

class TeacherAttendanceReportPage extends StatefulWidget {
  const TeacherAttendanceReportPage({super.key});

  @override
  State<TeacherAttendanceReportPage> createState() =>
      _TeacherAttendanceReportPageState();
}

class _TeacherAttendanceReportPageState
    extends State<TeacherAttendanceReportPage> {
  List attendance = [];

  int total = 0;
  int present = 0;
  int absent = 0;
  int late = 0;

  bool loading = true;

  Future<void> fetchReport() async {
    try {
      final response = await http.get(
        Uri.parse(
          'http://127.0.0.1:8000/api/teacher-attendance-report/',
        ),
      );

      final data = jsonDecode(response.body);

      if (data['success'] == true) {
        attendance = data['attendance'];
        total = data['total'];
        present = data['present'];
        absent = data['absent'];
        late = data['late'];
      }
    } catch (e) {
      print(e);
    }

    setState(() {
      loading = false;
    });
  }

  Color statusColor(String status) {
    if (status == 'Present') return Colors.greenAccent;
    if (status == 'Absent') return Colors.redAccent;
    if (status == 'Late') return Colors.orangeAccent;
    return Colors.white70;
  }

  Widget statCard(
    String title,
    int value,
    IconData icon,
    Color color,
  ) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.08),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white10),
        ),
        child: Column(
          children: [
            Icon(icon, color: color),
            const SizedBox(height: 8),
            Text(
              value.toString(),
              style: const TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.w900,
              ),
            ),
            Text(
              title,
              style: const TextStyle(color: Colors.white70),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    fetchReport();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),
      appBar: AppBar(
        title: const Text("Attendance Report"),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(18),
                  child: Row(
                    children: [
                      statCard("Total", total, Icons.list, Colors.blueAccent),
                      const SizedBox(width: 10),
                      statCard("Present", present, Icons.check_circle, Colors.greenAccent),
                    ],
                  ),
                ),

                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 18),
                  child: Row(
                    children: [
                      statCard("Absent", absent, Icons.cancel, Colors.redAccent),
                      const SizedBox(width: 10),
                      statCard("Late", late, Icons.access_time, Colors.orangeAccent),
                    ],
                  ),
                ),

                const SizedBox(height: 12),

                Expanded(
                  child: attendance.isEmpty
                      ? const Center(
                          child: Text(
                            "No attendance records",
                            style: TextStyle(color: Colors.white70),
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(18),
                          itemCount: attendance.length,
                          itemBuilder: (context, index) {
                            final item = attendance[index];

                            return Container(
                              margin: const EdgeInsets.only(bottom: 14),
                              padding: const EdgeInsets.all(18),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.08),
                                borderRadius: BorderRadius.circular(22),
                                border: Border.all(color: Colors.white10),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.analytics,
                                    color: statusColor(item['status']),
                                    size: 34,
                                  ),
                                  const SizedBox(width: 16),

                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          item['student_name'],
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontSize: 17,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          "Reg No: ${item['register_number']}",
                                          style: const TextStyle(
                                            color: Colors.white70,
                                          ),
                                        ),
                                        Text(
                                          "${item['subject']} • ${item['date']} ${item['time']}",
                                          style: const TextStyle(
                                            color: Colors.white70,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),

                                  Text(
                                    item['status'],
                                    style: TextStyle(
                                      color: statusColor(item['status']),
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }
}

class TeacherTimetablePage extends StatefulWidget {
  final String username;

  const TeacherTimetablePage({
    super.key,
    required this.username,
  });

  @override
  State<TeacherTimetablePage> createState() =>
      _TeacherTimetablePageState();
}

class _TeacherTimetablePageState
    extends State<TeacherTimetablePage> {
  List timetable = [];
  bool loading = true;

  Future<void> fetchTimetable() async {
    try {
      final response = await http.get(
        Uri.parse(
          'http://127.0.0.1:8000/api/teacher-timetable/?username=${widget.username}',
        ),
      );

      final data = jsonDecode(response.body);

      if (data['success'] == true) {
        timetable = data['timetable'];
      }
    } catch (e) {
      print(e);
    }

    setState(() {
      loading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    fetchTimetable();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),
      appBar: AppBar(
        title: const Text("Teacher Timetable"),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : timetable.isEmpty
              ? const Center(
                  child: Text(
                    "No timetable found",
                    style: TextStyle(color: Colors.white70),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(18),
                  itemCount: timetable.length,
                  itemBuilder: (context, index) {
                    final item = timetable[index];

                    return Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      padding: const EdgeInsets.all(18),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(22),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item['day'],
                            style: const TextStyle(
                              color: Colors.purpleAccent,
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            item['subject'],
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            "${item['start_time']} - ${item['end_time']}",
                            style: const TextStyle(color: Colors.white70),
                          ),
                          Text(
                            "${item['department']} - ${item['class_name']}",
                            style: const TextStyle(color: Colors.white70),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}

class FaceRecognitionPage extends StatefulWidget {
  final String teacherUsername;

  const FaceRecognitionPage({
    super.key,
    required this.teacherUsername,
  });

  @override
  State<FaceRecognitionPage> createState() => _FaceRecognitionPageState();
}

class _FaceRecognitionPageState extends State<FaceRecognitionPage> {
  CameraController? controller;

  bool loading = true;
  bool scanning = false;

  List timetable = [];
  List classes = [];
  List detectedStudents = [];

  String? selectedClassName;
  dynamic selectedTimetable;

  @override
  void initState() {
    super.initState();
    initCamera();
    fetchTimetable();
  }

  Future<void> initCamera() async {
    try {
      if (cameras.isEmpty) {
        cameras = await availableCameras();
      }

      if (cameras.isEmpty) {
        setState(() => loading = false);
        return;
      }

      controller = CameraController(
        cameras.first,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await controller!.initialize();

      setState(() => loading = false);
    } catch (e) {
      setState(() => loading = false);
    }
  }

  Future<void> fetchTimetable() async {
    try {
      final response = await http.get(
        Uri.parse(
          'http://127.0.0.1:8000/api/teacher-timetable/?username=${widget.teacherUsername}',
        ),
      );

      final data = jsonDecode(response.body);

      if (data['success'] == true) {
        timetable = data['timetable'];

        classes = timetable
            .map((item) => item['class_name'])
            .toSet()
            .toList();

        setState(() {});
      }
    } catch (e) {
      print(e);
    }
  }

  List get filteredTimetable {
    if (selectedClassName == null) return [];
    return timetable
        .where((item) => item['class_name'] == selectedClassName)
        .toList();
  }

  Future<void> scanFace() async {
    if (controller == null || !controller!.value.isInitialized) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Camera not ready")),
      );
      return;
    }

    if (selectedTimetable == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Select class and timetable")),
      );
      return;
    }

    setState(() {
      scanning = true;
      detectedStudents = [];
    });

    try {
      final image = await controller!.takePicture();
      final bytes = await image.readAsBytes();

      final base64Image =
          "data:image/jpeg;base64,${base64Encode(bytes)}";

      final response = await http.post(
        Uri.parse("http://127.0.0.1:8000/api/recognize-group/"),
        headers: {
          "Content-Type": "application/json",
        },
        body: jsonEncode({
          "image": base64Image,
          "subject_id": selectedTimetable['subject_id'],
        }),
      );

      final data = jsonDecode(response.body);

      if (data["success"] == true) {
        setState(() {
          detectedStudents = data["students"];
        });

        if (detectedStudents.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("No students detected")),
          );
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(data["message"] ?? "Recognition failed"),
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Camera scan failed: $e"),
        ),
      );
    }

    setState(() {
      scanning = false;
    });
  }

  Future<void> finalizeAttendance() async {
    if (selectedTimetable == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Select timetable first")),
      );
      return;
    }

    final detectedIds =
        detectedStudents.map((student) => student["id"]).toList();

    try {
      final response = await http.post(
        Uri.parse("http://127.0.0.1:8000/api/finalize-ai-attendance/"),
        headers: {
          "Content-Type": "application/json",
        },
        body: jsonEncode({
          "subject_id": selectedTimetable['subject_id'],
          "class_id": selectedTimetable['class_id'],
          "detected_ids": detectedIds,
        }),
      );

      final data = jsonDecode(response.body);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            data["success"] == true
                ? "Saved. Present: ${data['present_count']} | Absent: ${data['absent_count']}"
                : "Failed to save attendance",
          ),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Finalize failed: $e")),
      );
    }
  }

  InputDecoration inputStyle(String label) {
    return InputDecoration(
      labelText: label,
      labelStyle: const TextStyle(color: Colors.white70),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: Colors.white24),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(18),
        borderSide: const BorderSide(color: Colors.deepPurpleAccent),
      ),
    );
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xff0f172a),
      appBar: AppBar(
        title: const Text("Face Attendance"),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(18),
              child: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: selectedClassName,
                    dropdownColor: const Color(0xff1e293b),
                    decoration: inputStyle("Select Class"),
                    items: classes.map((className) {
                      return DropdownMenuItem<String>(
                        value: className,
                        child: Text(
                          className,
                          style: const TextStyle(color: Colors.white),
                        ),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedClassName = value;
                        selectedTimetable = null;
                        detectedStudents = [];
                      });
                    },
                  ),

                  const SizedBox(height: 16),

                  DropdownButtonFormField(
                    value: selectedTimetable,
                    dropdownColor: const Color(0xff1e293b),
                    decoration: inputStyle("Select Timetable"),
                    items: filteredTimetable.map((item) {
                      return DropdownMenuItem(
                        value: item,
                        child: Text(
                          "${item['day']} | ${item['subject']} | ${item['start_time']} - ${item['end_time']}",
                          style: const TextStyle(color: Colors.white),
                        ),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedTimetable = value;
                        detectedStudents = [];
                      });
                    },
                  ),

                  const SizedBox(height: 18),

                  if (controller != null && controller!.value.isInitialized)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: SizedBox(
                        height: 320,
                        width: double.infinity,
                        child: CameraPreview(controller!),
                      ),
                    )
                  else
                    Container(
                      height: 220,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: const Text(
                        "Camera not available",
                        style: TextStyle(color: Colors.white70),
                      ),
                    ),

                  const SizedBox(height: 18),

                  SizedBox(
                    width: double.infinity,
                    height: 55,
                    child: ElevatedButton.icon(
                      onPressed: scanning ? null : scanFace,
                      icon: const Icon(Icons.camera_alt),
                      label: Text(scanning ? "Scanning..." : "Scan Face"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.deepPurple,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),

                  const SizedBox(height: 14),

                  SizedBox(
                    width: double.infinity,
                    height: 55,
                    child: ElevatedButton.icon(
                      onPressed: finalizeAttendance,
                      icon: const Icon(Icons.check_circle),
                      label: const Text("Finalize Attendance"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  ...detectedStudents.map((student) {
                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: Colors.white10),
                      ),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.verified_user,
                            color: Colors.greenAccent,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              "${student['name']} - ${student['register_number']}",
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                ],
              ),
            ),
    );
  }
}


class LivelinessFaceUploadPage extends StatefulWidget {
  final String username;

  const LivelinessFaceUploadPage({
    super.key,
    required this.username,
  });

  @override
  State<LivelinessFaceUploadPage> createState() =>
      _LivelinessFaceUploadPageState();
}

class _LivelinessFaceUploadPageState
    extends State<LivelinessFaceUploadPage> {
  CameraController? controller;

  bool loading = true;
  bool uploading = false;

  bool autoCapturing = false;

  int capturedImages = 0;

  final int totalImages = 28;

  int step = 0;
  int uploadedCount = 0;

final List<Map<String, dynamic>> steps = [

  {
    "title": "Front Face",
    "subtitle": "Look straight at camera",
    "icon": Icons.face,
  },

  {
    "title": "Turn Left",
    "subtitle": "Turn your head LEFT",
    "icon": Icons.keyboard_arrow_left,
  },

  {
    "title": "Turn Right",
    "subtitle": "Turn your head RIGHT",
    "icon": Icons.keyboard_arrow_right,
  },

  {
    "title": "Look Up",
    "subtitle": "Move face UP",
    "icon": Icons.arrow_upward,
  },

  {
    "title": "Look Down",
    "subtitle": "Move face DOWN",
    "icon": Icons.arrow_downward,
  },

  {
    "title": "Smile",
    "subtitle": "Smile naturally",
    "icon": Icons.sentiment_satisfied_alt,
  },

  {
    "title": "Blink Eyes",
    "subtitle": "Blink your eyes",
    "icon": Icons.remove_red_eye,
  },

];
  @override
  void initState() {
    super.initState();
    initCamera();
  }

  Future<void> initCamera() async {
    try {
      if (cameras.isEmpty) {
        cameras = await availableCameras();
      }

      controller = CameraController(
        cameras.first,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await controller!.initialize();

      setState(() {
        loading = false;
      });
    } catch (e) {
      setState(() {
        loading = false;
      });
    }
  }

  Future<void> captureAndUpload() async {

    if (controller == null ||
        !controller!.value.isInitialized) {
      return;
    }

    setState(() {
      autoCapturing = true;
      uploading = true;
      capturedImages = 0;
      step = 0;
    });

    while (capturedImages < totalImages) {

      try {

        final image = await controller!.takePicture();

        final bytes = await image.readAsBytes();

        final base64Image =
            "data:image/jpeg;base64,${base64Encode(bytes)}";

        String expectedMove = "";

        if (step == 0) {
          expectedMove = "front";
        } else if (step == 1) {
          expectedMove = "left";
        } else if (step == 2) {
          expectedMove = "right";
        } else if (step == 3) {
          expectedMove = "up";
        } else if (step == 4) {
          expectedMove = "down";
        } else if (step == 5) {
          expectedMove = "smile";
        } else {
          expectedMove = "blink";
        }

        // REAL LIVELINESS VALIDATION

        final validationResponse = await http.post(

          Uri.parse(
            "http://127.0.0.1:8000/api/validate-liveliness/"
          ),

          headers: {
            "Content-Type": "application/json",
          },

          body: jsonEncode({

            "image": base64Image,
            "expected": expectedMove,

          }),
        );

        if (validationResponse.statusCode != 200) {
          print(validationResponse.body);
          continue;
        }

        Map<String, dynamic> validationData = {};

        try {
          validationData = jsonDecode(validationResponse.body);
        } catch (e) {
          print(validationResponse.body);
          continue;
        }

        // movement not detected
        if (validationData["success"] != true) {

          await Future.delayed(
            const Duration(milliseconds: 500),
          );

          continue;
        }

        // SAVE FACE

        final response = await http.post(

          Uri.parse(
            "http://127.0.0.1:8000/api/student-save-face/"
          ),

          headers: {
            "Content-Type": "application/json",
          },

          body: jsonEncode({

            "username": widget.username,
            "image": base64Image,
            "first_image": capturedImages == 0,

          }),
        );

        final data = jsonDecode(response.body);

        if (data["success"] == true) {

          setState(() {

            capturedImages++;

            // STEP CHANGES

            if (capturedImages < 4) {

              step = 0; // front

            } else if (capturedImages < 8) {

              step = 1; // left

            } else if (capturedImages < 12) {

              step = 2; // right

            } else if (capturedImages < 16) {

              step = 3; // up

            } else if (capturedImages < 20) {

              step = 4; // down

            } else if (capturedImages < 25) {

              step = 5; // smile

            } else {

              step = 6; // blink
            }
          });
        }

        await Future.delayed(
          const Duration(milliseconds: 500),
        );

      } catch (e) {

        print(e);
      }
    }

    setState(() {
      uploading = false;
      autoCapturing = false;
    });

    await trainModel();
  }
  Future<void> trainModel() async {

    try {

      final response = await http.post(

        Uri.parse(
          "http://127.0.0.1:8000/api/student-train-face/"
        ),

        headers: {
          "Content-Type": "application/json",
        },

        body: jsonEncode({
          "username": widget.username,
        }),
      );

      final data = jsonDecode(response.body);

      ScaffoldMessenger.of(context).showSnackBar(

        SnackBar(
          content: Text(
            data["message"] ??
            "Face model trained",
          ),
        ),
      );

      await Future.delayed(
        const Duration(seconds: 2),
      );

      Navigator.pushAndRemoveUntil(

        context,

        MaterialPageRoute(
          builder: (_) => StudentDashboard(
            username: widget.username,
          ),
        ),

        (route) => false,
      );

    } catch (e) {

      ScaffoldMessenger.of(context).showSnackBar(

        SnackBar(
          content: Text(
            "Training failed: $e",
          ),
        ),
      );
    }
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final current = steps[step];

    return Scaffold(
      backgroundColor: const Color(0xff0f172a),
      appBar: AppBar(
        title: const Text("Face Liveliness"),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(18),
              child: Column(
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(color: Colors.white10),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          current["icon"],
                          color: Colors.greenAccent,
                          size: 55,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          current["title"],
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 26,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          current["subtitle"],
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 15,
                          ),
                        ),
                        const SizedBox(height: 14),
                        Text(
                          "Step ${step + 1} of ${steps.length}",
                          style: const TextStyle(
                            color: Colors.greenAccent,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 18),

                  if (controller != null && controller!.value.isInitialized)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: SizedBox(
                        height: 340,
                        width: double.infinity,
                        child: CameraPreview(controller!),
                      ),
                    )
                  else
                    const Text(
                      "Camera not available",
                      style: TextStyle(color: Colors.white70),
                    ),

                  const SizedBox(height: 22),

                  LinearProgressIndicator(
                    value: (step + 1) / steps.length,
                    minHeight: 8,
                    backgroundColor: Colors.white12,
                    color: Colors.greenAccent,
                  ),
                  const SizedBox(height: 14),

                  Text(
                    "$capturedImages / $totalImages images captured",
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  const SizedBox(height: 22),

                  SizedBox(
                    width: double.infinity,
                    height: 55,
                    child: ElevatedButton.icon(
                      onPressed: uploading ? null : captureAndUpload,
                      icon: const Icon(Icons.camera_alt),
                      label: Text(
                        uploading
                            ? "Capturing Faces..."
                            : "Start AI Liveliness Capture",
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),

                  const SizedBox(height: 14),

                ],
              ),
            ),
    );
  }
}


