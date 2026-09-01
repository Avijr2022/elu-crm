// ignore_for_file: avoid_unnecessary_containers

import 'package:customertracker/user.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:dropdown_button2/dropdown_button2.dart';

class AddUser extends StatelessWidget {
  const AddUser({super.key});

  @override
  Widget build(BuildContext context) {
    const appTitle = 'Add User';
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
                    // Navigator.push(
                    //     context,
                    //     MaterialPageRoute(
                    //         builder: (context) => const UsersForm()));
                  },
                  child: const Icon(Icons.contact_phone_outlined),
                )),
            Padding(
                padding: const EdgeInsets.only(right: 20.0),
                child: GestureDetector(
                  onTap: () {
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const UsersForm()));
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

  // Dropdown 3.0+ explicit state control parameters setup
  final List<String> items = ['Admin', 'Manager', 'Employee', 'Guest'];
  String? selectedValue;
  late final ValueNotifier<String?> selectedValueNotifier;

  @override
  void initState() {
    super.initState();
    selectedValueNotifier = ValueNotifier<String?>(selectedValue);
    selectedValueNotifier.addListener(() {
      setState(() {
        selectedValue = selectedValueNotifier.value;
      });
    });
  }

  @override
  void dispose() {
    passwordController.dispose();
    selectedValueNotifier.dispose();
    super.dispose();
  }

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
                decoration: const BoxDecoration(),
                child: TextFormField(
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.person),
                    hintText: 'Enter your First Name',
                    labelText: 'First Name',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(),
                child: const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.person),
                    hintText: 'Enter your Last Name',
                    labelText: 'Last Name',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(),
                child: const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(FontAwesomeIcons.userTie),
                    hintText: 'Enter your Designation',
                    labelText: 'Designation',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(),
                child: const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.email),
                    hintText: 'Enter a email address',
                    labelText: 'Email',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                decoration: const BoxDecoration(),
                child: const TextField(
                  decoration: InputDecoration(
                    prefixIcon: Icon(Icons.phone),
                    hintText: 'Enter a phone number',
                    labelText: 'Phone',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                child: TextField(
                  obscureText: true,
                  controller: passwordController,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.key),
                    suffixIcon: Icon(Icons.remove_red_eye),
                    hintText: 'Enter a password',
                    labelText: 'Password',
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                height: 50,
                child: DropdownButtonHideUnderline(
                  child: DropdownButton2<String>(
                    isExpanded: true,
                    hint: Text(
                      'Select Role',
                      style: TextStyle(
                        fontSize: 20,
                        color: Theme.of(context).hintColor,
                      ),
                    ),
                    items: items
                        .map((item) => DropdownItem<String>(
                              value: item,
                              height:
                                  40, // Height explicitly configured inside items loop syntax
                              child: Text(
                                item,
                                style: const TextStyle(fontSize: 14),
                              ),
                            ))
                        .toList(),
                    valueListenable: selectedValueNotifier,
                    dropdownStyleData: const DropdownStyleData(
                      maxHeight: 200,
                    ),
                    menuItemStyleData: const MenuItemStyleData(),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
