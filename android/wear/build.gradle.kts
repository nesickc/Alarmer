plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "io.github.nesickc.alarmer.wear"
    // Compose 1.12 needs 37 to compile against; targetSdk decides runtime behaviour.
    compileSdk = 37

    defaultConfig {
        // Same id as :phone. The Data Layer only connects apps with the same package name and signature.
        applicationId = "io.github.nesickc.alarmer"
        minSdk = 34
        targetSdk = 36
        versionCode = 1
        versionName = "0.0.1"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    implementation(project(":shared"))
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.foundation)
    implementation(libs.wear.compose.material3)
    implementation(libs.activity.compose)
}
