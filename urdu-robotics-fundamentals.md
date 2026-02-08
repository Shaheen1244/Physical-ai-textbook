---
sidebar_position: 2
---

# روبوٹکس کی مبادیات (Robotics Fundamentals in Urdu)

## روبوٹ کی اجزاء (Robot Components)

ہر روبوٹ کے چند بنیادی اجزاء ہوتے ہیں:

### سینسر (Sensors)
- **کیمرے** (Cameras): دیکھنے کے لیے
- **لیزر رینجرز** (Laser Range Finders): فاصلہ پیمائی کے لیے
- **جیرو سکوپس** (Gyroscopes): توازن کے لیے

### ایکٹو ایٹرز (Actuators)
- **موٹرز** (Motors): حرکت کے لیے
- **سروو** (Servos): محدود حرکت کے لیے
- **ہائیڈرولکس** (Hydraulics): طاقتور حرکت کے لیے

## روبوٹکس کے کام (Robot Functions)

### 1. سینسینگ (Sensing)
ربوٹ اپنے ماحول کو سمجھتا ہے:

```python
# مثال کے طور پر (Example)
def read_sensors():
    camera_data = camera.read()
    lidar_data = lidar.read()
    return camera_data, lidar_data
```

### 2. پلاننگ (Planning)
ربوٹ اپنے کام کا منصوبہ بناتا ہے:

- کہاں جانا ہے؟
- رکاوٹوں سے کیسے بچنا ہے؟
- کیسے کام کرنا ہے؟

### 3. کنٹرول (Control)
ربوٹ اپنے ایکٹو ایٹرز کو کنٹرول کرتا ہے:

- موٹر کو چلانا
- ہاتھ کو حرکت دینا
- اشیاء کو اٹھانا

## روبوٹکس کی قسمیں (Types of Robots)

- **انڈسٹریل روبوٹس** (Industrial Robots): کارخانوں میں
- **سروس روبوٹس** (Service Robots): انسانوں کی مدد کے لیے
- **ریسرچ روبوٹس** (Research Robots): تحقیق کے لیے
- **ہوم روبوٹس** (Home Robots): گھر میں استعمال کے لیے

## مستقبل میں روبوٹکس (Robotics in Future)

مستقبل میں روبوٹس انسانوں کے قریب تر ہوں گے اور ان کی زندگی میں مددگار ثابت ہوں گے۔