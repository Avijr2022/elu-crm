// ignore_for_file: sized_box_for_whitespace

import 'package:customertracker/edit_profile.dart';
import 'package:flutter/material.dart';

import 'side_menu_app.dart';

// ignore_for_file: camel_case_types
class myprofile extends StatelessWidget {
  const myprofile({super.key});

  // This widget is the root of the application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My Profile',
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        drawer: const NavDrawer(),
        appBar: AppBar(
          actions: <Widget>[
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const Editprofile()));
                  },
                  child: const Icon(Icons.edit),
                )),
          ],
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          title: const Text('My Profile'),
        ),
        body: Container(
          padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
          height: 1000,
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/cover.jpg'),
              fit: BoxFit.cover,
            ),
          ),
          child: ListView(
            children: <Widget>[
              Container(
                height: 250,
                // decoration: const BoxDecoration(
                //   gradient: LinearGradient(
                //     colors: [
                //       Color.fromARGB(255, 214, 214, 135),
                //       Color.fromARGB(255, 235, 235, 126)
                //     ],
                //     begin: Alignment.centerLeft,
                //     end: Alignment.centerRight,
                //     stops: [0.5, 0.9],
                //   ),
                // ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: <Widget>[
                        CircleAvatar(
                          backgroundColor: Color.fromARGB(255, 214, 214, 135),
                          minRadius: 0.0,
                          child: Icon(
                            Icons.call,
                            size: 30.0,
                            color: Color.fromARGB(255, 56, 55, 55),
                          ),
                        ),
                        CircleAvatar(
                          backgroundColor: Color.fromARGB(179, 255, 255, 255),
                          minRadius: 45.0,
                          child: CircleAvatar(
                              radius: 40.0,
                              backgroundImage:
                                  AssetImage('assets/images/kedargupta.jpg')
                              // NetworkImage(''),
                              ),
                        ),
                        CircleAvatar(
                          backgroundColor: Color.fromARGB(255, 214, 214, 126),
                          minRadius: 20.0,
                          child: Icon(
                            Icons.message,
                            size: 30.0,
                            color: Color.fromARGB(255, 56, 55, 55),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(
                      height: 10,
                    ),
                    Text(
                      'Kedar Gupta',
                      style: TextStyle(
                        fontSize: 25,
                        fontWeight: FontWeight.bold,
                        color: Color.fromARGB(255, 56, 55, 55),
                      ),
                    ),
                    Text(
                      'Business Development',
                      style: TextStyle(
                        color: Color.fromARGB(255, 56, 55, 55),
                        fontSize: 20,
                      ),
                    ),
                    Text(
                      '94326 47740',
                      style: TextStyle(
                        color: Color.fromARGB(255, 56, 55, 55),
                        fontSize: 15,
                      ),
                    ),
                    Text(
                      'Euphoria Infotech',
                      style: TextStyle(
                        color: Color.fromARGB(255, 56, 55, 55),
                        fontSize: 12,
                      ),
                    ),
                    Text(
                      'Euphoriainfotech@org.co.in',
                      style: TextStyle(
                        color: Color.fromARGB(255, 56, 55, 55),
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              Row(
                children: <Widget>[
                  Expanded(
                    child: Container(
                      color: const Color.fromARGB(100, 112, 112, 111),
                      child: const ListTile(
                        title: Text(
                          '300',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                            color: Color.fromARGB(255, 59, 58, 58),
                          ),
                        ),
                        subtitle: Text(
                          'Leads',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 20,
                            color: Color.fromARGB(255, 56, 55, 55),
                          ),
                        ),
                      ),
                    ),
                  ),
                  Expanded(
                    child: Container(
                      color: const Color.fromARGB(255, 214, 214, 126),
                      child: const ListTile(
                        title: Text(
                          '159',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                            color: Color.fromARGB(2255, 56, 55, 55),
                          ),
                        ),
                        subtitle: Text(
                          'Following',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 20,
                            color: Color.fromARGB(255, 56, 55, 55),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const Column(
                children: <Widget>[
                  ListTile(
                    tileColor: Color.fromARGB(255, 214, 214, 135),
                    title: Text(
                      'Address Line1',
                      style: TextStyle(
                        color: Color.fromARGB(255, 91, 92, 92),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      'EM 3, BENGAL ECO INTELIGENT PARK',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                  ),
                  Divider(),
                  ListTile(
                    tileColor: Color.fromARGB(255, 214, 214, 135),
                    title: Text(
                      'Address Line2',
                      style: TextStyle(
                        color: Color.fromARGB(255, 91, 92, 92),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      'EM Block, Sector V, Salt Lake City',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                  ),
                  Divider(),
                  ListTile(
                    tileColor: Color.fromARGB(255, 214, 214, 135),
                    title: Text(
                      'City',
                      style: TextStyle(
                        color: Color.fromARGB(255, 91, 92, 92),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      'Kolkata',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                  ),
                  Divider(),
                  ListTile(
                    tileColor: Color.fromARGB(255, 214, 214, 135),
                    title: Text(
                      'State',
                      style: TextStyle(
                        color: Color.fromARGB(255, 91, 92, 92),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      'West Bengal',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                  ),
                  Divider(),
                  ListTile(
                    tileColor: Color.fromARGB(255, 214, 214, 135),
                    title: Text(
                      'ZIP',
                      style: TextStyle(
                        color: Color.fromARGB(255, 91, 92, 92),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      '700091',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                  ),
                  Divider(),
                  ListTile(
                    tileColor: Color.fromARGB(255, 214, 214, 135),
                    title: Text(
                      'Email',
                      style: TextStyle(
                        color: Color.fromARGB(255, 91, 92, 92),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      'mail2kedargupta@gmail.com',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                  ),
                  Divider(),
                  ListTile(
                    tileColor: Color.fromARGB(255, 214, 214, 135),
                    title: Text(
                      'GitHub',
                      style: TextStyle(
                        color: Color.fromARGB(255, 91, 92, 92),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      'https://github.com/kedargupta',
                      style: TextStyle(
                        fontSize: 15,
                      ),
                    ),
                  ),
                  Divider(),
                  ListTile(
                    tileColor: Color.fromARGB(255, 214, 214, 135),
                    title: Text(
                      'Linkedin',
                      style: TextStyle(
                        color: Color.fromARGB(255, 91, 92, 92),
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      'https://www.linkedin.com/in/kedar-gupta-aa671789',
                      style: TextStyle(
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}
