#ifndef LIBRARY_SPECULAR

#define PI 3.14159265359

// Calcula a refletância especular da superfície utilizando o modelo de Blinn-Phong inserido na BRDF
vec3 specularReflectance(vec3 fresnel, vec3 normal, vec3 halfAngle, vec3 viewDirection, vec3 lightDirection, float roughness)
{
    // 1. Mapeamento de rugosidade para o expoente de brilho (alpha)
    float smoothness = 1.0 - roughness;
    float alpha = pow(8192.0, smoothness);

    // 2. Produtos escalares (dot products) limitados para não ficarem negativos
    float NdotH = max(dot(normal, halfAngle), 0.0);
    
    // O 0.001 no NdotV evita artefatos escuros nas bordas do objeto
    float NdotV = max(dot(normal, viewDirection), 0.001); 
    float NdotL = max(dot(normal, lightDirection), 0.0);

    // 3. Fator de normalização de energia matemática
    float energyConservation = (alpha + 2.0) / (8.0 * PI);

    // 4. Denominador da função Cook-Torrance
    // Usa 0.00001 como trava extra de segurança contra divisão por zero
    float denominator = max(NdotV * NdotL, 0.00001);

    // 5. Calcula o lóbulo especular
    float spec = pow(NdotH, alpha) * energyConservation;

    // Retorna a composição final da BRDF Especular
    return (fresnel * spec) / denominator;
}

#define LIBRARY_SPECULAR
#endif