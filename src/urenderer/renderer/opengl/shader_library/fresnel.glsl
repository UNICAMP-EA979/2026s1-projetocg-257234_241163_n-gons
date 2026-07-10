#ifndef LIBRARY_FRESNEL

/// Calcula a refletância de Fresnel
vec3 fresnelReflectance(vec3 baseColor, float metallic, vec3 halfAngle, vec3 lightDirection)
{
    // F0: Refletância base (0.04 para materiais dielétricos, ou a própria cor base para metais)
    vec3 F0 = mix(vec3(0.04), baseColor, metallic);
    
    // O cosseno do ângulo de incidência no micro-nível
    float cosTheta = max(dot(halfAngle, lightDirection), 0.0);
    
    // Aproximação de Schlick para o efeito Fresnel
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

#define LIBRARY_FRESNEL
#endif