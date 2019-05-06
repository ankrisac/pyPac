#ifdef GL_ES
precision highp float;
precision highp int;
#endif

uniform sampler2D texture;
uniform vec2 texOffset;

varying vec4 vertColor;
varying vec4 vertTexCoord;



float offset(float x, float scale){
    return scale * (pow(2 * x - 1, 2) - 1);
}

void main() {
    vec2 p0 = vertTexCoord.xy - vec2(0.0, 0.5);
    float x1 = offset(p0.x, 0.05);
    
    vec2 pos = vertTexCoord.xy + vec2(0, p0.y*x1);
    
    vec4 col = vec4(0.0, 0.0, 0.0, 1.0);
    if(0.0 <= pos.x && pos.x <= 1.0 && 0.0 <= pos.y && pos.y <= 1.0){
        col = texture2D(texture, pos.xy);
    }

    gl_FragColor = col;
}
