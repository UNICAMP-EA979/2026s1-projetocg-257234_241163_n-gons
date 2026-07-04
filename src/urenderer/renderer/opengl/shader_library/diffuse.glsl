#ifndef LIBRARY_DIFUSE

#define PI 3.14159265359

//Calcula a refletância difusa da superfície utilizando o modelo de Lambert
vec3 diffuseReflectance(vec3 fresnel, vec3 baseColor, float metallic)
{
    vec3 diffuse = (1 - fresnel) * baseColor / PI;
    diffuse = diffuse * (1 - metallic);

    return diffuse;
}

#define LIBRARY_DIFUSE
#endif