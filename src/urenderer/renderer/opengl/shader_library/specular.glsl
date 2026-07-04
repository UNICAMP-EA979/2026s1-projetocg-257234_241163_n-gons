#ifndef LIBRARY_SPECULAR

#define PI 3.14159265359

//Calcula a refletância especular da superfície utilizando o modelo de Blinn-Phong
vec3 specularReflectance(vec3 fresnel, vec3 normal, vec3 halfAngle, vec3 viewDirection, vec3 LightDirection, float roughness)
{
    float normalhalf = max(dot(halfAngle, normal), 0);
    float normalview = max(dot(normal, viewDirection), 0);
    float normalLight = max(dot(normal, LightDirection), 0);

    float smoothness = 1 - roughness;
    float alpha = pow(8192, smoothness);

    vec3 specular = fresnel;
    specular *= (alpha + 2) / (8 * PI);
    specular *= pow(normalhalf, alpha);
    specular /= max(normalview * normalLight, 0.0001);

    return specular;
}

#define LIBRARY_SPECULAR
#endif