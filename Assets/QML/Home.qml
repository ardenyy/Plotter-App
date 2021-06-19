import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

Item {
    property bool isStreaming: true
    property bool isCameraOpen: true
    property bool isSelectingPort: false
    property bool isPlotting: false
    property string buttonCameraText: qsTr("Take a Photo")
    property string buttonRetakeText: qsTr("Retake")
    property string buttonProcessText: qsTr("Process the Photo")
    property string buttonPlotText: qsTr("Start Plotting the Image")

    Connections{
        target: presenter
        function onNewFrame() {
            image.reload()
        }
        function onStartedStreaming() {
            isStreaming = true
            isCameraOpen = true
            isSelectingPort = false
            isPlotting = false
            console.log("Started Streaming")
        }
        function onFinishedStreaming() {
            isStreaming = false
            isCameraOpen = true
            isSelectingPort = false
            isPlotting = false
            console.log("Finished Streaming")
        }
        function onCameraClosed() {
            isStreaming = false
            isCameraOpen = false
            isSelectingPort = true
            isPlotting = false
            console.log("Camera Closed")
        }
        function onPlottingStarted() {
            isStreaming = false
            isCameraOpen = false
            isSelectingPort = false
            isPlotting = true
            buttonRetake.enabled = false
            console.log("Started Plotting")
        }
        function onPlottingStopped() {
            buttonRetake.enabled = true
            console.log("Finished Plotting")
        }
        function onProgressUpdate(progress) {
            circularProgress.currentValue = progress
            circularProgress.text = progress.toFixed(2) + "%"
            if(progress === 100) delay(2000, circularProgress.text = "DONE!")
        }
        function onSerialPorts(ports) {
            portModel.clear()
            portModel.append({text: ports})
            comboBoxSerial.model = portModel
        }
        function onConnectionTimeout(error) {
            console.log(error)
            buttonRetake.clicked()
        }
    }

    function delay(delayTime, cb) {
        timer.interval = delayTime;
        timer.repeat = false;
        timer.triggered.connect(cb);
        timer.start();
    }

    ListModel {
        id: portModel
    }

    Rectangle {
        id: rectangle
        anchors.fill: parent
        color: "#054854"
        border.color: "#53565A"
        border.width: 5
        clip: true

        Image {
            id: background
            source: "../tdu_background.png"
            anchors.fill: parent
            anchors.margins: parent.border.width
            z: 0
        }

        Image {
            id: tdu_logo
            source: "../tdu_logo.png"
            antialiasing: true
            sourceSize.width: 100
            sourceSize.height: 100
            mipmap: true
            width: parent.width / 10
            height: width
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: 15
            z: 0
        }

        Image {
            id: tub_logo
            source: "../tub_logo.png"
            antialiasing: true
            sourceSize.width: 100
            sourceSize.height: 100
            mipmap: true
            width: parent.width / 10
            height: width
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 15
            z: 0
        }

        Rectangle {
            id: imageRectangle
            width: 0.6*rectangle.width
            height: (1/1.414)*width // "A" paper ratio
            visible: !isPlotting
            anchors.top: parent.top
            anchors.topMargin: 50
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 50
            color: "#0096b4"
            radius: 10
            z: 1

            Image {
                id: image
                source: "image://camera_provider/frame"
                anchors.margins: 10
                sourceSize.width: parent.width
                sourceSize.height: (1/1.414)*sourceSize.width // "A" paper ratio
                cache: false
                smooth: true
                anchors.fill: parent
                property bool counter: false
                function reload(){
                    counter = !counter
                    source = "image://camera_provider/frame?id=" + counter
                }
            }

            MouseArea {
                anchors.fill: parent
                onClicked: presenter.openPreviewImage(rectangle.width, rectangle.height)
            }
        }

        CircularProgress {
            id: circularProgress
            anchors.top: parent.top
            visible: isPlotting
            anchors.topMargin: 50
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 50
            width: 0.45*parent.width
            height: width
            z: 1
        }

        Row {
            id: row
            spacing: 20
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 50
            anchors.top: imageRectangle.bottom
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 50
            height: children.height
            z: 1

            RoundButton {
                id: buttonCamera
                visible: isStreaming
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                text: buttonCameraText
                onClicked: presenter.stopCamera()
                background: Rectangle {
                    color: "#53565A"
                    radius: parent.padding
                    opacity: 0.5
                    border.width: 3
                    border.color: "#000000"
                }
            }

            RoundButton {
                id: buttonRetake
                visible: !isStreaming
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                text: buttonRetakeText
                onClicked: {
                    presenter.startCamera()
                }
                background: Rectangle {
                    color: "#53565A"
                    radius: parent.padding
                    opacity: 0.5
                    border.width: 3
                    border.color: "#000000"
                }
            }

            RoundButton {
                id: buttonProcess
                visible: !isStreaming && isCameraOpen
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                text: buttonProcessText
                onClicked: presenter.processImage()
                background: Rectangle {
                    color: "#53565A"
                    radius: parent.padding
                    opacity: 0.5
                    border.width: 3
                    border.color: "#000000"
                }
            }

            ComboBox {
                id:comboBoxSerial
                visible: isSelectingPort
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                background: Rectangle {
                    color: "#53565A"
                    radius: parent.padding
                    opacity: 0.5
                    border.width: 3
                    border.color: "#000000"
                }
            }

            RoundButton {
                id: buttonPlot
                visible: isSelectingPort
                height: 55
                width: implicitWidth + rectangle.width/10
                padding: 15
                text: buttonPlotText
                onClicked: {
                    presenter.startPlotting(comboBoxSerial.currentText)
                }
                background: Rectangle {
                    color: "#53565A"
                    radius: parent.padding
                    opacity: 0.5
                    border.width: 3
                    border.color: "#000000"
                }
            }
        }
    }
}
