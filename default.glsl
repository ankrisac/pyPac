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
    int lines = 1000;
    float bLine = 5;
    float lineSpaceRatio = 0.75;
    int num_col = 16;

    vec4 col = texture2D(texture, vertTexCoord.xy);
    
    if(mod(vertTexCoord.y * lines, bLine) >= (bLine * lineSpaceRatio)){
        round_color(col, num_col, col);
        gl_FragColor = col * vec4(0.8, 1.0, 0.8, 1.0);
    }
    else{
        gl_FragColor = col * vec4(0.8, 1.0, 0.8, 1.0) * 0.5;
    }
}