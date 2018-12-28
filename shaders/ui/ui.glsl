#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

uniform sampler2D texture;
uniform vec2 texOffset;

varying vec4 vertColor;
varying vec4 vertTexCoord;


void round_col(in float in_col, in float num, in float out_col){
    out_col = round(in_col * num) / num;
}

void round_color(in vec4 in_color, in float num_color, out vec4 out_color){
    round_col(in_color.x, num_color, out_color.x);
    round_col(in_color.y, num_color, out_color.y);
    round_col(in_color.z, num_color, out_color.z);
    out_color.w = 1.0;
}

void offset(in float x, in float scale, out float X){
    X = scale*(pow(2*x - 1, 2) - 1);
}

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