import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:newton_particles/newton_particles.dart';
import 'package:animated_text_kit/animated_text_kit.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Music Information Retrieval',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const FirstPage(),
    );
  }
}

class FirstPage extends StatefulWidget {
  const FirstPage({super.key});

  @override
  State<FirstPage> createState() => _FirstPageState();
}

class _FirstPageState extends State<FirstPage> {
  final _recorder = AudioRecorder();
  //late Record _recorder;
  late AudioPlayer player = AudioPlayer();
  bool _isRecording = false;
  String? _audioPath;
  Timer? timer;
  Duration duration = Duration.zero;

  @override
  void initState() {
    super.initState();
    player = AudioPlayer();
    //_recorder = Record();
  }

  void _startTimer() {
    timer = Timer.periodic(const Duration(seconds: 1), (Timer timer) {
      setState(() {
        duration = duration + const Duration(seconds: 1);
      });
    });
  }

  void _stopTimer() {
    timer?.cancel(); // Stop the timer
    setState(() {
      duration = Duration.zero; // Reset the duration
    });
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      _stop();
      print('stop recording');
    } else {
      _start();
      print('start recording');
    }
  }

  Future<bool> _checkPermission() async {
    if (await Permission.storage.isGranted &&
        await Permission.microphone.isGranted) {
      if (Platform.isAndroid &&
          await Permission.manageExternalStorage.isGranted) {
        return true;
      }
      return true;
    }
    return false;
  }

  Future<bool> _requestPermission() async {
    if (Platform.isAndroid && await Permission.manageExternalStorage.isDenied) {
      // Show a dialog asking the user to allow storage management permission
      bool manageStorageGranted = await _showManageStorageDialog();
      if (!manageStorageGranted) return false;
    }

    var status = await [Permission.microphone, Permission.manageExternalStorage]
        .request();

    return status[Permission.microphone] == PermissionStatus.granted &&
        status[Permission.manageExternalStorage] == PermissionStatus.granted;
  }

  Future<bool> _showManageStorageDialog() async {
    return await showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              title: const Text('Storage Permission Needed'),
              content: const Text(
                  'This app needs access to your storage to save audio recordings. Please grant storage permission.'),
              actions: <Widget>[
                TextButton(
                  child: const Text('Cancel'),
                  onPressed: () {
                    Navigator.of(context).pop(false);
                  },
                ),
                TextButton(
                  child: Text('Allow'),
                  onPressed: () async {
                    Navigator.of(context).pop(true);
                    await Permission.manageExternalStorage.request();
                  },
                ),
              ],
            );
          },
        ) ??
        false;
  }

  Future<void> _start() async {
    // Check permissions
    bool hasPermission = await _checkPermission();

    if (!hasPermission) {
      // Request permissions
      hasPermission = await _requestPermission();

      if (!hasPermission) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
                'Microphone and storage permissions are required to start recording.'),
          ),
        );
        return;
      }
    }

    // Permissions are granted, proceed with accessing the Download directory
    Directory? dir = await getExternalStorageDirectory();
    if (dir != null) {
      Directory downloadDir = Directory('${dir.path}/Download');
      if (!await downloadDir.exists()) {
        await downloadDir.create(recursive: true);
      }

      String fileName =
          'recording_${DateTime.now().millisecondsSinceEpoch}.m4a';
      String fullPath = '${downloadDir.path}/$fileName';

      // Start recording
      await _recorder.start(const RecordConfig(), path: fullPath);
      setState(() {
        _isRecording = true;
        _audioPath =
            fullPath; // Assume recording starts immediately for UI feedback
        _startTimer();
      });
      print('Recording started and saving to $fullPath');
    } else {
      print('Could not access external storage directory');
    }
  }

  Future<void> _stop() async {
    try {
      if (!_isRecording) {
        print('Recording is not in progress, skipping stop command');
        return;
      }
      print('Stop method called');
      String? path = await _recorder.stop();
      print('Recording stopped, file saved at $path');
      _stopTimer();
      setState(() {
        _isRecording = false;
        _audioPath = path!;
        duration = Duration.zero; // Reset the duration
      });
    } catch (e) {
      print('An error occurred while stopping the recording: $e');
    }
  }

  // Navigate to the ProcessingPage
  void _navigateToProcessingPage(BuildContext context) async {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const ProcessingPage(),
      ),
    );

    // Upload the audio file
    await _uploadAudio(context);
  }

  // Play Audio
  Future<void> _playAudio() async {
    if (_audioPath == null) {
      print('No recorded audio to play');
      return;
    }
    try {
      print('audio is played');
      Source urlSource = UrlSource(_audioPath!);
      await player.play(urlSource); // For newer versions of audioplayers
      // For older versions, it might just be: await player.play(_audioPath, isLocal: true);
    } catch (e) {
      print('An error occurred while playing the audio: $e');
    }
  }

  // upload audio here
  Future<void> _uploadAudio(BuildContext context) async {
    if (_audioPath == null) {
      print('No audio to upload');
      return;
    }

    try {
      final request = http.MultipartRequest(
        'PUT',
        Uri.parse(
            'https://ea36-175-139-75-146.ngrok-free.app/upload'), // Use Ngrok URL here
      );
      request.files.add(await http.MultipartFile.fromPath('file', _audioPath!));
      final response = await request.send();

      if (response.statusCode == 200) {
        final respStr = await response.stream.bytesToString();
        final jsonResponse = jsonDecode(respStr);
        print('Prediction: ${jsonResponse['top_5_predictions']}');

        // Navigate to the results page and pass the predictions
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => ResultsPage(
                youtubeResults: List<Map<String, dynamic>>.from(
                    jsonResponse['youtube_results']),
                predictions:
                    List<String>.from(jsonResponse['top_5_predictions'])),
          ),
        );
      } else {
        print('Failed to upload audio');
      }
    } catch (e) {
      print('An error occurred while uploading the audio: $e');
    }
  }

  @override
  void dispose() {
    super.dispose();
    timer?.cancel();
    _recorder.dispose();
    player.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Music Information Retrieval'),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Placeholder(
                fallbackHeight: 50, fallbackWidth: double.infinity),
            const SizedBox(height: 20),
            Text(
              _isRecording
                  ? '${duration.inHours.toString().padLeft(2, '0')}:${duration.inMinutes.remainder(60).toString().padLeft(2, '0')}:${duration.inSeconds.remainder(60).toString().padLeft(2, '0')}'
                  : '00:00:00',
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                  backgroundColor: _isRecording ? Colors.red : Colors.green,
                  foregroundColor: Colors.white),
              onPressed: _toggleRecording,
              child: Icon(_isRecording ? Icons.stop : Icons.mic, size: 50),
            ),
            const SizedBox(height: 20), // Add some spacing
            // Playback button
            ElevatedButton(
              onPressed: _audioPath == null
                  ? null
                  : _playAudio, // Disable button if _audioPath is null
              style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue, foregroundColor: Colors.white),
              child: const Text('Play Recording'),
            ),
            ElevatedButton(
              onPressed: _audioPath == null
                  ? null
                  : () => _navigateToProcessingPage(context),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
              child: const Text('Done'),
            )
          ],
        ),
      ),
    );
  }
}

class ProcessingPage extends StatefulWidget {
  const ProcessingPage({super.key});

  @override
  State<ProcessingPage> createState() => _ProcessingPageState();
}

class _ProcessingPageState extends State<ProcessingPage> {
  @override
  Widget build(BuildContext context) {
    final Size screenSize = MediaQuery.of(context).size;
    final Offset center = Offset(screenSize.width / 2, screenSize.height / 2.8);
    return Scaffold(
      appBar: AppBar(),
      body: Stack(
        children: [
          Center(
            child: Newton(
              activeEffects: [
                PulseEffect(
                  particleConfiguration: ParticleConfiguration(
                    shape: CircleShape(),
                    size: const Size(8, 8),
                    color: const LinearInterpolationParticleColor(colors: [
                      Color.fromARGB(255, 4, 8, 90),
                      Color.fromARGB(255, 68, 44, 185),
                      Color.fromRGBO(27, 206, 173, 1)
                    ]),
                  ),
                  effectConfiguration: EffectConfiguration(
                    maxDuration: 4524,
                    minDuration: 3497,
                    particlesPerEmit: 35,
                    emitCurve: Curves.bounceOut,
                    emitDuration: 1051,
                    fadeOutCurve: Curves.bounceIn,
                    fadeInCurve: Curves.bounceOut,
                    minEndScale: 0.5,
                    maxEndScale: 2.5,
                    origin: center,
                  ),
                ),
              ],
            ),
          ),
          Positioned(
            bottom: 280, // Adjust this value to move the text higher or lower
            left: 0,
            right: 0,
            child: Center(
              child: AnimatedTextKit(
                animatedTexts: [
                  TyperAnimatedText(
                    'Processing...',
                    textStyle: const TextStyle(
                      fontSize: 42.0,
                      fontWeight: FontWeight.bold,
                      color: Color.fromARGB(255, 11, 45, 72),
                    ),
                    speed: const Duration(milliseconds: 500),
                  ),
                ],
                totalRepeatCount: 50,
                pause: const Duration(milliseconds: 500),
                displayFullTextOnTap: false,
                stopPauseOnTap: false,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class ResultsPage extends StatefulWidget {
  final List<String> predictions;
  final List<Map<String, dynamic>> youtubeResults;

  const ResultsPage({
    super.key,
    required this.youtubeResults,
    required this.predictions,
  });

  @override
  State<ResultsPage> createState() => _ResultsPageState();
}

class _ResultsPageState extends State<ResultsPage> {
  late final List<Map<String, dynamic>> youtubeResults;
  late final List<String> predictions;

  @override
  void initState() {
    super.initState();
    youtubeResults = widget.youtubeResults;
    predictions = widget.predictions;
  }

  void _launchURL(String videoId) async {
    final Uri url = Uri.parse('https://www.youtube.com/watch?v=$videoId' as String);
    if (await canLaunchUrl(url)) {
      await launchUrl(url);
    } else {
      throw 'Could not launch $url';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Results')),
      body: ListView.builder(
        itemCount: widget.youtubeResults.length,
        itemBuilder: (context, index) {
          final result = widget.youtubeResults[index];
          return ListTile(
            leading: result.containsKey('thumbnail') ? Image.network(result['thumbnail']) : null,
            title: result.containsKey('title') ? Text(result['title']) : const Text('No title'),
            subtitle: result.containsKey('description') ? Text(result['description']) : const Text('No description'),
            onTap: () {
              if (result.containsKey('videoId')) {
                _launchURL(result['videoId']);
              } else {
                print('No video ID available');
              }
            },
          );
        },
      ),
    );
  }
}
