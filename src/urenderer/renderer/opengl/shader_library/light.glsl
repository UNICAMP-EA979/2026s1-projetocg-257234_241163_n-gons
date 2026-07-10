#ifndef LIBRARY_LIGHT

const int LIGHT_UNSET = 0;
const int LIGHT_DIRECTIONAL = 1;
const int LIGHT_POINT = 2;
const float R_MIN = 0.05;

struct Light
{
    int type;
    vec3 color;
    float intensity;
    vec3 direction; // Only directional
    vec3 position; // Only point
    float reference_distance; // Only point
};

// Calcula a atenuação da luz
float computeLightAttenuation(Light light, vec3 position)
{
    if(light.type == LIGHT_DIRECTIONAL)
    {
        return light.intensity;
    }
    else
    {
        // Distância do fragmento até a luz
        float r = distance(light.position, position);
        
        // Lei do inverso do quadrado
        return light.intensity * pow(light.reference_distance / max(r, R_MIN), 2.0);
    }

}

// Calcula a direção da luz
vec3 computeLightDirection(Light light, vec3 position)
{
    if(light.type == LIGHT_DIRECTIONAL)
    {
        return normalize(light.direction);
    }
    else
    {
        // Vetor que aponta do fragmento para a luz pontual
        return normalize(light.position - position);
    }
}

#define LIBRARY_LIGHT
#endif