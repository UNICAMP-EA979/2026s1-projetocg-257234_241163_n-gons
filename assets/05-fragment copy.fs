#version 330 core

#include "light.glsl"
#include "fresnel.glsl"
#include "diffuse.glsl"
#include "specular.glsl"

#define MAX_LIGHT 10
#define PI 3.14159265359

in vec3 worldPosition;
in vec3 worldNormal;
in vec2 uv;

uniform vec3 ambientColor;
uniform sampler2D baseColorTexture;
uniform sampler2D metallicTexture;
uniform sampler2D roughnessTexture;
uniform float tiling = 1.0;
uniform mat4 viewTransformation; // Necessário para extrair a posição da câmera

out vec4 FragColor;

uniform Light lights[MAX_LIGHT];

void main()
{
    // Calcule a normal do fragmento de forma normalizada
    vec3 worldNormalNormalized = normalize(worldNormal);

    // Calcule a direção de visualização (saindo do ponto)
    vec3 cameraPosition = vec3(inverse(viewTransformation) * vec4(0.0, 0.0, 0.0, 1.0));
    vec3 viewDirection = normalize(cameraPosition - worldPosition);

    // Calcule a uv com tiling
    vec2 uvTiling = uv * tiling;

    // Realize sampling das texturas para obter as propriedades da superfície.
    // Usamos .r para metallic e roughness, pois armazenam informações de apenas 1 canal (escala de cinza).
    vec3 baseColor = texture(baseColorTexture, uvTiling).rgb;
    float metallic = texture(metallicTexture, uvTiling).r;
    float roughness = texture(roughnessTexture, uvTiling).r;

    // Calcule a luz ambiente baseada na textura
    // Calcule a luz ambiente anulando a cor difusa em materiais metálicos
    vec3 ambientLightContribution = ambientColor * baseColor * (1.0 - metallic);

    // Inicializa a cor com a luz ambiente
    vec3 color = ambientLightContribution;

    for(int i = 0; i < MAX_LIGHT; i++)
    {
        Light light = lights[i];
        if(light.type == LIGHT_UNSET)
        {
            break;
        }

        // Calcule dados da luz (atenuação, cor, direção)
        float attenuation = computeLightAttenuation(light, worldPosition);
        vec3 lightColor = light.color * light.intensity;
        vec3 lightDirection = computeLightDirection(light, worldPosition);

        // Calcule o half-angle
        vec3 halfAngle = normalize(lightDirection + viewDirection);

        // Calcule as refletâncias de fresnel, difusa e especular
        vec3 fresnel = fresnelReflectance(baseColor, metallic, halfAngle, lightDirection);
        vec3 diffuse = diffuseReflectance(fresnel, baseColor, metallic);
        vec3 specular = specularReflectance(fresnel, worldNormalNormalized, halfAngle, viewDirection, lightDirection, roughness);

        // Calcule a refletância final
        vec3 reflectance = diffuse + specular;

        // Calcule a contribuição da luz e acumule na color
        float NdotL = max(dot(worldNormalNormalized, lightDirection), 0.0);
        vec3 lightContribution = reflectance * lightColor * attenuation * NdotL;
        
        color += lightContribution;
    }

    // A conversão final de linear para sRGB é garantida pela engine (GL_FRAMEBUFFER_SRGB)
    FragColor = vec4(color, 1.0);
}