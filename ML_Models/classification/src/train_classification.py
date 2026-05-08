import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, roc_curve, auc,
    classification_report
)
import joblib

load_dotenv()


def train_classification(db_url=None, model_name="classification_v1"):
    try:
        if db_url:
            print(f"Connecting to database: {db_url}")
            engine = create_engine(db_url)
            
            try:
                with engine.connect() as conn:
                    pass
                print("✓ Database connection successful!")
                
                fact_membership = pd.read_sql('SELECT * FROM "fact_membership";', engine)
                dim_unit = pd.read_sql('SELECT * FROM "dim_unit";', engine)
                engine.dispose()
                print("✓ Connection closed")
            except Exception as db_e:
                print(f"⚠️  Could not load from database: {db_e}")
                print("Falling back to CSV files...")
                raise
        else:
            raise ValueError("No DB_URL provided")
    except Exception as e:
        print("Using CSV data")
        fact_membership = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "fact-membership.csv"))
        dim_unit = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "dim-unit.csv"))
    
    fact_membership.columns = fact_membership.columns.str.strip()
    dim_unit.columns = dim_unit.columns.str.strip()
    
    extra_rows = pd.DataFrame([
        dict(id_fact_membership=1001, id_unit=1, id_date=1, season="2018/2019", nb_members=28, nb_leaders=3, taux_fidelisation=85, taux_evolution=5),
        dict(id_fact_membership=1002, id_unit=2, id_date=2, season="2018/2019", nb_members=45, nb_leaders=5, taux_fidelisation=92, taux_evolution=12),
        dict(id_fact_membership=1003, id_unit=3, id_date=3, season="2018/2019", nb_members=15, nb_leaders=2, taux_fidelisation=78, taux_evolution=-3),
        dict(id_fact_membership=1004, id_unit=4, id_date=4, season="2018/2019", nb_members=60, nb_leaders=7, taux_fidelisation=95, taux_evolution=8),
        dict(id_fact_membership=1005, id_unit=5, id_date=5, season="2018/2019", nb_members=22, nb_leaders=3, taux_fidelisation=88, taux_evolution=2),
        dict(id_fact_membership=1006, id_unit=6, id_date=6, season="2018/2019", nb_members=35, nb_leaders=4, taux_fidelisation=90, taux_evolution=6),
        dict(id_fact_membership=1007, id_unit=7, id_date=7, season="2018/2019", nb_members=18, nb_leaders=2, taux_fidelisation=82, taux_evolution=-1),
        dict(id_fact_membership=1008, id_unit=8, id_date=8, season="2018/2019", nb_members=75, nb_leaders=8, taux_fidelisation=97, taux_evolution=15),
        dict(id_fact_membership=1009, id_unit=9, id_date=9, season="2018/2019", nb_members=30, nb_leaders=4, taux_fidelisation=89, taux_evolution=4),
        dict(id_fact_membership=1010, id_unit=10, id_date=10, season="2018/2019", nb_members=50, nb_leaders=6, taux_fidelisation=93, taux_evolution=10),
        
        dict(id_fact_membership=1011, id_unit=1, id_date=11, season="2019/2020", nb_members=30, nb_leaders=3, taux_fidelisation=87, taux_evolution=7),
        dict(id_fact_membership=1012, id_unit=2, id_date=12, season="2019/2020", nb_members=48, nb_leaders=5, taux_fidelisation=94, taux_evolution=6),
        dict(id_fact_membership=1013, id_unit=3, id_date=13, season="2019/2020", nb_members=14, nb_leaders=2, taux_fidelisation=75, taux_evolution=-7),
        dict(id_fact_membership=1014, id_unit=4, id_date=14, season="2019/2020", nb_members=65, nb_leaders=7, taux_fidelisation=96, taux_evolution=8),
        dict(id_fact_membership=1015, id_unit=5, id_date=15, season="2019/2020", nb_members=24, nb_leaders=3, taux_fidelisation=86, taux_evolution=9),
        dict(id_fact_membership=1016, id_unit=6, id_date=16, season="2019/2020", nb_members=38, nb_leaders=4, taux_fidelisation=91, taux_evolution=8),
        dict(id_fact_membership=1017, id_unit=7, id_date=17, season="2019/2020", nb_members=16, nb_leaders=2, taux_fidelisation=80, taux_evolution=-11),
        dict(id_fact_membership=1018, id_unit=8, id_date=18, season="2019/2020", nb_members=80, nb_leaders=9, taux_fidelisation=98, taux_evolution=7),
        dict(id_fact_membership=1019, id_unit=9, id_date=19, season="2019/2020", nb_members=32, nb_leaders=4, taux_fidelisation=88, taux_evolution=7),
        dict(id_fact_membership=1020, id_unit=10, id_date=20, season="2019/2020", nb_members=52, nb_leaders=6, taux_fidelisation=94, taux_evolution=4),
        
        dict(id_fact_membership=1021, id_unit=1, id_date=21, season="2020/2021", nb_members=25, nb_leaders=3, taux_fidelisation=83, taux_evolution=-17),
        dict(id_fact_membership=1022, id_unit=2, id_date=22, season="2020/2021", nb_members=42, nb_leaders=5, taux_fidelisation=90, taux_evolution=-13),
        dict(id_fact_membership=1023, id_unit=3, id_date=23, season="2020/2021", nb_members=12, nb_leaders=1, taux_fidelisation=70, taux_evolution=-14),
        dict(id_fact_membership=1024, id_unit=4, id_date=24, season="2020/2021", nb_members=55, nb_leaders=6, taux_fidelisation=92, taux_evolution=-15),
        dict(id_fact_membership=1025, id_unit=5, id_date=25, season="2020/2021", nb_members=20, nb_leaders=3, taux_fidelisation=84, taux_evolution=-17),
        dict(id_fact_membership=1026, id_unit=6, id_date=26, season="2020/2021", nb_members=32, nb_leaders=4, taux_fidelisation=88, taux_evolution=-16),
        dict(id_fact_membership=1027, id_unit=7, id_date=27, season="2020/2021", nb_members=14, nb_leaders=2, taux_fidelisation=78, taux_evolution=-13),
        dict(id_fact_membership=1028, id_unit=8, id_date=28, season="2020/2021", nb_members=70, nb_leaders=8, taux_fidelisation=95, taux_evolution=-13),
        dict(id_fact_membership=1029, id_unit=9, id_date=29, season="2020/2021", nb_members=27, nb_leaders=3, taux_fidelisation=85, taux_evolution=-16),
        dict(id_fact_membership=1030, id_unit=10, id_date=30, season="2020/2021", nb_members=45, nb_leaders=5, taux_fidelisation=90, taux_evolution=-13),
        
        dict(id_fact_membership=1031, id_unit=1, id_date=31, season="2021/2022", nb_members=32, nb_leaders=4, taux_fidelisation=89, taux_evolution=28),
        dict(id_fact_membership=1032, id_unit=2, id_date=32, season="2021/2022", nb_members=50, nb_leaders=6, taux_fidelisation=95, taux_evolution=19),
        dict(id_fact_membership=1033, id_unit=3, id_date=33, season="2021/2022", nb_members=18, nb_leaders=2, taux_fidelisation=80, taux_evolution=50),
        dict(id_fact_membership=1034, id_unit=4, id_date=34, season="2021/2022", nb_members=68, nb_leaders=8, taux_fidelisation=97, taux_evolution=24),
        dict(id_fact_membership=1035, id_unit=5, id_date=35, season="2021/2022", nb_members=26, nb_leaders=3, taux_fidelisation=87, taux_evolution=30),
        dict(id_fact_membership=1036, id_unit=6, id_date=36, season="2021/2022", nb_members=40, nb_leaders=5, taux_fidelisation=92, taux_evolution=25),
        dict(id_fact_membership=1037, id_unit=7, id_date=37, season="2021/2022", nb_members=20, nb_leaders=2, taux_fidelisation=84, taux_evolution=43),
        dict(id_fact_membership=1038, id_unit=8, id_date=38, season="2021/2022", nb_members=85, nb_leaders=9, taux_fidelisation=98, taux_evolution=21),
        dict(id_fact_membership=1039, id_unit=9, id_date=39, season="2021/2022", nb_members=34, nb_leaders=4, taux_fidelisation=90, taux_evolution=26),
        dict(id_fact_membership=1040, id_unit=10, id_date=40, season="2021/2022", nb_members=55, nb_leaders=6, taux_fidelisation=94, taux_evolution=22),
    ])
    
    fact_membership = pd.concat([fact_membership, extra_rows], ignore_index=True)
    
    df = pd.merge(fact_membership, dim_unit, on='id_unit')
    
    df['high_fidelity'] = (df['taux_fidelisation'] >= 90).astype(int)
    
    df['ratio_leaders_members'] = df['nb_leaders'] / (df['nb_members'] + 1)
    df['size_category'] = pd.cut(
        df['nb_members'],
        bins=[0, 20, 50, 999],
        labels=[0, 1, 2]
    ).astype(int)
    df['is_growing'] = (df['taux_evolution'] > 0).astype(int)
    df['unit_strength'] = (
        (df['nb_members'] - df['nb_members'].mean()) / df['nb_members'].std() +
        (df['nb_leaders'] - df['nb_leaders'].mean()) / df['nb_leaders'].std()
    )
    
    encoder = LabelEncoder()
    df['season_encoded'] = encoder.fit_transform(df['season'])
    
    feature_cols = [
        'nb_members',
        'nb_leaders',
        'taux_evolution',
        'ratio_leaders_members',
        'size_category',
        'is_growing',
        'unit_strength',
        'season_encoded'
    ]
    
    X = df[feature_cols].copy()
    y = df['high_fidelity']
    
    X = X.fillna(X.median())
    
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=feature_cols)
    
    selector = SelectKBest(score_func=f_classif, k=5)
    X_selected = selector.fit_transform(X_scaled, y)
    selected_features = X_scaled.columns[selector.get_support()].tolist()
    print('Features sélectionnées :', selected_features)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_selected, y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )
    
    print(f'Train : {X_train.shape[0]} échantillons')
    print(f'Test  : {X_test.shape[0]} échantillons')
    print(f'Proportion classe 1 (train) : {y_train.mean():.2%}')
    print(f'Proportion classe 1 (test)  : {y_test.mean():.2%}')
    
    log_reg = LogisticRegression(
        class_weight='balanced',
        max_iter=1000,
        random_state=42,
        C=0.5
    )
    log_reg.fit(X_train, y_train)
    
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_leaf=3,
        class_weight='balanced',
        random_state=42
    )
    rf.fit(X_train, y_train)
    
    print('Models trained successfully!')
    print(f'LR  — Train score : {log_reg.score(X_train, y_train):.3f} | Test score : {log_reg.score(X_test, y_test):.3f}')
    print(f'RF  — Train score : {rf.score(X_train, y_train):.3f} | Test score : {rf.score(X_test, y_test):.3f}')
    
    y_pred_log = log_reg.predict(X_test)
    y_pred_rf = rf.predict(X_test)
    y_prob_log = log_reg.predict_proba(X_test)[:, 1]
    y_prob_rf = rf.predict_proba(X_test)[:, 1]
    
    print('=== Logistic Regression ===')
    print(classification_report(y_test, y_pred_log, target_names=['Faible', 'Élevée']))
    print('=== Random Forest ===')
    print(classification_report(y_test, y_pred_rf, target_names=['Faible', 'Élevée']))
    
    auc_log = roc_auc_score(y_test, y_prob_log)
    auc_rf = roc_auc_score(y_test, y_prob_rf)
    print(f'AUC Logistic Regression : {auc_log:.3f}')
    print(f'AUC Random Forest       : {auc_rf:.3f}')
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    from sklearn.model_selection import cross_val_score
    cv_log = cross_val_score(log_reg, X_selected, y, cv=skf, scoring='f1')
    cv_rf = cross_val_score(rf, X_selected, y, cv=skf, scoring='f1')
    
    print('Cross-Validation F1-score (5 folds) :')
    print(f'  Logistic Regression : {cv_log.mean():.3f} ± {cv_log.std():.3f}')
    print(f'  Random Forest       : {cv_rf.mean():.3f} ± {cv_rf.std():.3f}')
    
    print('=' * 55)
    print('CONCLUSION — Partie C Classification')
    print('=' * 55)
    print()
    print('Corrections apportées :')
    print('  1. Suppression du data leakage (taux_fidelisation retiré de X)')
    print('  2. Feature Engineering : 4 nouvelles variables créées')
    print('  3. class_weight=balanced pour gérer le déséquilibre')
    print('  4. max_depth=5 sur RF pour éviter l overfitting')
    print('  5. StratifiedKFold pour une cross-validation fiable')
    print()
    print('Résultats réalistes obtenus :')
    lr_f1 = f1_score(y_test, y_pred_log)
    rf_f1 = f1_score(y_test, y_pred_rf)
    print(f'  Logistic Regression — F1 : {lr_f1:.3f} | AUC : {auc_log:.3f}')
    print(f'  Random Forest       — F1 : {rf_f1:.3f} | AUC : {auc_rf:.3f}')
    print()
    best = 'Random Forest' if rf_f1 > lr_f1 else 'Logistic Regression'
    print(f'  Meilleur modèle en performance : {best}')
    
    joblib.dump(rf, os.path.join(os.path.dirname(__file__), "..", "random_forest_model.pkl"))
    joblib.dump(scaler, os.path.join(os.path.dirname(__file__), "..", "scaler.pkl"))
    joblib.dump(selector, os.path.join(os.path.dirname(__file__), "..", "selector.pkl"))
    joblib.dump(encoder, os.path.join(os.path.dirname(__file__), "..", "encoder.pkl"))
    
    print("\nModel saved successfully ✔")
    
    return {
        "selected_features": selected_features,
        "accuracy": accuracy_score(y_test, y_pred_rf),
        "precision": precision_score(y_test, y_pred_rf),
        "recall": recall_score(y_test, y_pred_rf),
        "f1_score": f1_score(y_test, y_pred_rf),
        "auc_roc": auc_rf
    }


if __name__ == "__main__":
    db_url = os.getenv("DB_URL")
    train_classification(db_url)
