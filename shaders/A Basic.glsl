#ifdef GL_ES
precision highp float;
precision highp int;
#endif

uniform sampler2D texture;
uniform vec2 texOffset;

varying vec4 vertColor;
varying vec4 vertTexCoord;


void main() {
    float x0 = vertTexCoord.x;
    float y0 = vertTexCoord.y - 0.5;
    float h = 1;

    float x1 = 0;
    
    vec2 pos = vertTexCoord.xy + vec2(0, y0*x1);
    vec4 col = vec4(0.0, 0.0, 0.0, 1.0);

    if(0.0 <= pos.x && pos.x <= 1.0 && 0.0 <= pos.y && pos.y <= 1.0){
        col = texture2D(texture, pos.xy);
    }

    gl_FragColor = col;
}
