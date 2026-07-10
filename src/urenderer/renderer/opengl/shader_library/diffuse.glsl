#ifndef LIBRARY_DIFUSE

#define PI 3.14159265359

// Calcula a refletância difusa da superfície utilizando o modelo de Lambert
vec3 diffuseReflectance(vec3 fresnel, vec3 baseColor, float metallic)
{
    // Conservação de energia: a luz que não sofreu reflexão de Fresnel entra na superfície
    vec3 kD = vec3(1.0) - fresnel;
    
    // Superfícies puramente metálicas não possuem cor difusa
    kD *= 1.0 - metallic;
    
    // Modelo Lambertiano (espalhamento uniforme no hemisfério dividido por PI)
    return kD * (baseColor / PI);
}

#define LIBRARY_DIFUSE
#endif