#ifdef GL_ES
precision highp float;
precision highp int;
#endif

uniform sampler2D texture;
uniform vec2 texOffset;

varying vec4 vertColor;
varying vec4 vertTexCoord;


void main() {
    int lines = 1000;
    float bLine = 5;
    float lineSpaceRatio = 0.75;
    int num_col = 16;

    vec4 col = (texture2D(texture, vertTexCoord.xy + vec2(texOffset.x, 0)) + texture2D(texture, vertTexCoord.xy + vec2(-texOffset.x, 0))
             + texture2D(texture, vertTexCoord.xy + vec2(0, texOffset.y)) + texture2D(texture, vertTexCoord.xy + vec2(0, -texOffset.x)))/4;
    
    if(mod(vertTexCoord.y * lines, bLine) >= (bLine * lineSpaceRatio)){
        gl_FragColor = col * vec4(0.8, 1.0, 0.8, 1.0);
    }
    else{
        gl_FragColor = col * vec4(0.8, 1.0, 0.8, 1.0) * 0.5;
    }
}
