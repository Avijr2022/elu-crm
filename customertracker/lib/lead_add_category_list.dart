// ignore_for_file: avoid_unnecessary_containers, unused_import

import 'package:customertracker/lead_category.dart';
import 'package:customertracker/user.dart';
import 'package:flutter/material.dart';

class AddLeadCategoryList extends StatelessWidget {
  const AddLeadCategoryList({super.key});

  @override
  Widget build(BuildContext context) {
    const appTitle = 'Create List';
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: appTitle,
      home: Scaffold(
        resizeToAvoidBottomInset: true,
        appBar: AppBar(
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          actions: <Widget>[
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const LeadCategoryForm()));
                  },
                  child: const Icon(Icons.add_task),
                )),
          ],
          title: const Text(
            appTitle,
          ),
          leading: IconButton(
              onPressed: () {
                Navigator.pop(context);
              },
              icon: const Icon(
                Icons.arrow_back_ios,
                size: 20,
                color: Color.fromARGB(255, 252, 250, 250),
              )),
        ),
        body: Container(
          padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
          height: 1000,
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/cover2.jpg'),
              fit: BoxFit.cover,
            ),
          ),
          child: const MyCustomForm(),
        ),
      ),
    );
  }
}

class MyCustomForm extends StatefulWidget {
  const MyCustomForm({super.key});

  @override
  MyCustomFormState createState() {
    return MyCustomFormState();
  }
}

class MyCustomFormState extends State<MyCustomForm> {
  final _formKey = GlobalKey<FormState>();
  TextEditingController passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Container(
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Container(
                decoration: const BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage('assets/images/cover.jpg'),
                    fit: BoxFit.cover,
                  ),
                  color: Color.fromARGB(100, 229, 238, 144),
                ),
                child: const CircleAvatar(
                  backgroundColor: Color.fromARGB(100, 229, 238, 144),
                  minRadius: 44.0,
                  child: Center(
                    child: CircleAvatar(
                      radius: 38.0,
                      backgroundColor: Color.fromARGB(100, 220, 228, 149),
                      backgroundImage: null,
                      child: ClipOval(
                        child: SizedBox(
                          width: 180.0,
                          height: 180.0,
                          child: Icon(Icons.camera_alt),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              const Divider(
                color: Color.fromARGB(255, 91, 92, 92),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(
                    // color: Color.fromARGB(255, 214, 214, 135),
                    ),
                child: TextFormField(
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.format_list_bulleted_sharp),
                    // hintText: 'Enter your First Name',
                    labelText: 'List Name',
                  ),
                ),
              ),
              const SizedBox(height: 30),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 5.0),
                alignment: Alignment.topLeft,
                // margin: const EdgeInsets.all(20),
                height: 60,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: const Color.fromARGB(57, 255, 255, 255),
                  borderRadius: BorderRadius.circular(5), //border corner radius
                  boxShadow: [
                    BoxShadow(
                      color: const Color.fromARGB(52, 158, 158, 158)
                          .withOpacity(0.2), //color of shadow
                      spreadRadius: 5, //spread radius
                      blurRadius: 7, // blur radius
                      offset: const Offset(0, 2), // changes position of shadow
                      //first paramerter of offset is left-right
                      //second parameter is top to down
                    ),
                    //you can set more BoxShadow() here
                  ],
                ),
                child: TextFormField(
                  decoration: const InputDecoration(
                    suffixIcon: Icon(Icons.info_outline),
                    // hintText: 'Enter your First Name',
                    labelText: 'Auto-response',
                  ),
                ),
                // const Text(
                //   "Auto-response",
                //   style: TextStyle(
                //     fontSize: 14,
                //   ),
                // ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 5.0),
                alignment: Alignment.topLeft,
                // margin: const EdgeInsets.all(20),
                height: 60,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: const Color.fromARGB(57, 255, 255, 255),
                  borderRadius: BorderRadius.circular(3), //border corner radius
                  boxShadow: [
                    BoxShadow(
                      color: const Color.fromARGB(52, 158, 158, 158)
                          .withOpacity(0.0), //color of shadow
                      spreadRadius: 5, //spread radius
                      blurRadius: 7, // blur radius
                      offset: const Offset(0, 2), // changes position of shadow
                      //first paramerter of offset is left-right
                      //second parameter is top to down
                    ),
                    //you can set more BoxShadow() here
                  ],
                ),
                child: TextFormField(
                  decoration: const InputDecoration(
                    prefix: Icon(Icons.email_outlined),
                    suffixIcon: Icon(
                      Icons.toggle_off_outlined,
                      size: 50,
                    ),
                    // hintText: 'Enter your First Name',
                    labelText: 'Send greeting email',
                  ),
                ),
                // const Text(
                //   "Auto-response",
                //   style: TextStyle(
                //     fontSize: 14,
                //   ),
                // ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
