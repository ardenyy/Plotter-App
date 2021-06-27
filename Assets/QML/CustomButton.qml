import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls.Material.impl 2.15
import QtGraphicalEffects 1.15

RoundButton {
    id: customButton
    background: Rectangle {
        color: "#53565A"
        radius: parent.padding
        opacity: 0.5
        border.width: 3
        border.color: "#000000"
    }
    Ripple {
        id: ripple
        anchors.fill: parent
        clipRadius: parent.padding
        pressed: parent.pressed
        active: parent.down || parent.visualFocus || parent.hovered
        color: "#9053565A"
        layer.enabled: true
        layer.effect: OpacityMask {
            maskSource: Rectangle {
                width: ripple.width
                height: ripple.height
                radius: ripple.clipRadius
            }
        }
    }
}
